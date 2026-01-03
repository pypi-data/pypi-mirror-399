import numpy as np
import librosa
import os
import json
import time
from rknnlite.api import RKNNLite


class Workflow:
    def __init__(self, model_path=None, smoothing_time_constant=0, step_size=43):
        self.rknn_lite = None
        self.classes = []  # 只保留类别标签
        self.metadata = {}
        self.model_params = {
            'fft_size': 2048,
            'sample_rate': 44100,
            'num_frames': 43,  # 每块帧数
            'spec_features': 232  # 频谱特征数
        }
        self.smoothing_time_constant = smoothing_time_constant
        self.step_size = step_size
        self.frame_duration = None
        self.hop_length = 735  # 44100/60=735 (每帧时长 ~16.67ms)
        self.previous_spec = None
        self.input_shape = [1, 232, 1, 43]  # RKNN模型输入形状

        if model_path:
            self.load_model(model_path)

        # 计算帧时间信息
        self.frame_duration = self.hop_length / self.model_params['sample_rate']
        self.block_duration = self.model_params['num_frames'] * self.frame_duration

    def load_model(self, model_path):
        """加载RKNN模型并仅解析classes元数据"""
        try:
            self.rknn_lite = RKNNLite()
            
            # 加载RKNN模型
            ret = self.rknn_lite.load_rknn(model_path)
            if ret != 0:
                raise RuntimeError(f'加载RKNN模型失败, 错误码: {ret}')
            
            # 初始化运行时环境
            ret = self.rknn_lite.init_runtime()
            if ret != 0:
                raise RuntimeError(f'初始化NPU运行时失败, 错误码: {ret}')
            
            # 加载元数据（仅提取classes）
            metadata_path = self._get_metadata_path(model_path)
            self._load_metadata(metadata_path)
            
            print(f"使用指定输入形状: {self.input_shape}")
            
        except Exception as e:
            print(f"模型加载失败: {e}")

    def _get_metadata_path(self, model_path):
        """获取元数据文件路径"""
        base_dir = os.path.dirname(model_path)
        base_name = os.path.basename(model_path)
        metadata_name = os.path.splitext(base_name)[0] + '_metadata.json'
        metadata_path = os.path.join(base_dir, metadata_name)
        
        if not os.path.exists(metadata_path):
            metadata_path = os.path.join(base_dir, 'rknn_metadata.json')
            
        return metadata_path

    def _load_metadata(self, metadata_path):
        """仅从JSON文件加载classes元数据"""
        self.classes = []  # 初始化为空列表
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                # 只提取classes，忽略其他元数据
                self.classes = metadata.get('classes', [])
                print(f"从 {metadata_path} 加载类别标签成功，共 {len(self.classes)} 个类别")
            else:
                print(f"元数据文件 {metadata_path} 不存在，将使用空类别标签")
        except Exception as e:
            print(f"加载元数据失败: {e}，将使用空类别标签")

    def _apply_hann_window(self, frame):
        """应用汉宁窗函数"""
        return frame * np.hanning(len(frame))

    def _apply_temporal_smoothing(self, current_spec):
        """应用时域指数平滑"""
        if self.previous_spec is None:
            self.previous_spec = current_spec
            return current_spec

        smoothed = (self.smoothing_time_constant * self.previous_spec
                    + (1 - self.smoothing_time_constant) * current_spec)

        self.previous_spec = smoothed.copy()
        return smoothed

    def _load_audio(self, audio_path):
        """加载音频文件（支持wav和webm）"""
        ext = os.path.splitext(audio_path)[1].lower()

        if ext == '.wav':
            audio, sr = librosa.load(audio_path, sr=self.model_params['sample_rate'])
            return audio, sr

        elif ext == '.webm':
            try:
                from pydub import AudioSegment
            except ImportError:
                raise ImportError("处理webm格式需要pydub库，请先安装：pip install pydub")

            try:
                audio_segment = AudioSegment.from_file(audio_path, format='webm')
                audio_segment = audio_segment.set_channels(1).set_frame_rate(self.model_params['sample_rate'])
                samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                return samples / 32768.0, self.model_params['sample_rate']  # 归一化到[-1, 1]
            except FileNotFoundError as e:
                if 'ffmpeg' in str(e).lower() or 'avconv' in str(e).lower():
                    print("\n" + "="*60)
                    print("检测到错误：缺少ffmpeg支持，无法处理webm格式音频")
                    print("="*60)
                    print("请安装ffmpeg后重试（参考之前的安装指南）")
                    print("="*60 + "\n")
                    raise
                else:
                    raise
            except Exception as e:
                print(f"处理webm音频时发生错误：{str(e)}")
                raise

        else:
            raise ValueError(f"不支持的音频格式: {ext}，目前支持 .wav 和 .webm")

    def _preprocess_audio(self, audio_path):
        """预处理音频文件，返回[232, 时间帧]形状的分贝谱"""
        audio, sr = self._load_audio(audio_path)
        assert sr == self.model_params['sample_rate'], f"采样率不匹配，需要 {self.model_params['sample_rate']}Hz"

        # 计算STFT
        hop_length = self.hop_length
        win_length = self.model_params['fft_size']
        n_fft = self.model_params['fft_size']

        # 分帧并加窗
        frames = librosa.util.frame(audio, frame_length=win_length, hop_length=hop_length)
        windowed_frames = np.zeros_like(frames)
        for i in range(frames.shape[1]):
            windowed_frames[:, i] = self._apply_hann_window(frames[:, i])

        # FFT+幅度谱+分贝转换
        D = np.fft.rfft(windowed_frames, n=n_fft, axis=0)
        magnitude = np.abs(D)
        db = 20 * np.log10(np.maximum(1e-5, magnitude))  # 避免log(0)

        # 截取特征维度，返回[232, 时间帧]
        return db[:self.model_params['spec_features'], :]

    def preprocess_audio_segment(self, audio_segment):
        """预处理音频片段，返回[232, 时间帧]形状的分贝谱"""
        # 计算STFT（逻辑与_preprocess_audio一致）
        hop_length = self.hop_length
        win_length = self.model_params['fft_size']
        n_fft = self.model_params['fft_size']

        frames = librosa.util.frame(audio_segment, frame_length=win_length, hop_length=hop_length)
        windowed_frames = np.zeros_like(frames)
        for i in range(frames.shape[1]):
            windowed_frames[:, i] = self._apply_hann_window(frames[:, i])

        D = np.fft.rfft(windowed_frames, n=n_fft, axis=0)
        magnitude = np.abs(D)
        db = 20 * np.log10(np.maximum(1e-5, magnitude))

        return db[:self.model_params['spec_features'], :]

    def _extract_blocks(self, full_spec):
        """从完整频谱中提取[232, 43]的块"""
        total_time_frames = full_spec.shape[1]
        blocks = []
        start_indices = []

        num_blocks = (total_time_frames - self.model_params['num_frames']) // self.step_size + 1

        for i in range(num_blocks):
            start = i * self.step_size
            end = start + self.model_params['num_frames']
            block = full_spec[:, start:end]  # 提取[232, 43]的块

            # 不足43帧时填充
            if block.shape[1] < self.model_params['num_frames']:
                padded = np.zeros((self.model_params['spec_features'], self.model_params['num_frames']))
                padded[:, :block.shape[1]] = block
                block = padded

            blocks.append(block)
            start_indices.append(start)

        return blocks, start_indices

    def _normalize(self, spec):
        """简化归一化：仅使用当前频谱块的均值和方差"""
        epsilon = 1e-8
        mean = np.mean(spec)
        variance = np.var(spec)
        std = np.sqrt(variance)
        return ((spec - mean) / (std + epsilon)).astype(np.float32)

    def inference(self, audio_path, model_path=None):
        if model_path and not self.rknn_lite:
            self.load_model(model_path)

        full_spec = self._preprocess_audio(audio_path)  # 形状[232, 总时间帧]
        blocks, start_indices = self._extract_blocks(full_spec)

        block_results = []

        print(f"开始处理音频: {audio_path}")
        print(f"总帧数: {full_spec.shape[1]}, 总时长: {full_spec.shape[1] * self.frame_duration:.2f}秒")
        print(f"将处理 {len(blocks)} 个块 (每块 {self.model_params['num_frames']}帧 = {self.block_duration:.3f}秒)")
        print("=" * 60)

        for i, block in enumerate(blocks):
            start_time = time.time()

            # 归一化+调整维度至[1, 232, 1, 43]
            normalized_block = self._normalize(block)
            input_tensor = normalized_block[:, np.newaxis, :]  # [232, 1, 43]
            input_tensor = input_tensor[np.newaxis, ...]       # [1, 232, 1, 43]

            # RKNN推理
            outputs = self.rknn_lite.inference(inputs=[input_tensor])
            raw_output = outputs[0][0]
            result = self._format_output(raw_output)

            # 记录结果
            process_time = time.time() - start_time
            start_frame = start_indices[i]
            end_frame = start_frame + self.model_params['num_frames']
            start_time_sec = start_frame * self.frame_duration
            end_time_sec = end_frame * self.frame_duration

            block_results.append({
                'block_index': i,
                'start_time': start_time_sec,
                'end_time': end_time_sec,
                'process_time': process_time,
                'result': result,
                'raw_output': raw_output
            })

            print(f"块 #{i+1} [时间: {start_time_sec:.2f}-{end_time_sec:.2f}s]")
            print(f"  分类: {result['class']}, 置信度: {result['confidence']}%")
            print(f"  处理时间: {process_time * 1000:.2f}ms")
            print("-" * 50)

        final_result = self._aggregate_results(block_results)
        return block_results, final_result
        
    def process_audio_segment(self, audio_segment):
        """处理音频片段（实时处理），包含时间测量功能"""
        if not self.rknn_lite:
            raise ValueError("请先加载模型")
            
        # 记录总开始时间
        total_start_time = time.time()
        
        # 记录预处理时间
        preprocess_start_time = time.time()
        full_spec = self.preprocess_audio_segment(audio_segment)
        blocks, start_indices = self._extract_blocks(full_spec)
        preprocess_time = time.time() - preprocess_start_time

        block_results = []
        inference_time = 0.0
        
        for i, block in enumerate(blocks):
            # 记录归一化时间
            normalize_start_time = time.time()
            normalized_block = self._normalize(block)
            input_tensor = normalized_block[:, np.newaxis, :][np.newaxis, ...]  # [1, 232, 1, 43]
            normalize_time = time.time() - normalize_start_time
            
            # 记录推理时间
            inference_start_time = time.time()
            outputs = self.rknn_lite.inference(inputs=[input_tensor])
            block_inference_time = time.time() - inference_start_time
            inference_time += block_inference_time
            
            raw_output = outputs[0][0]
            result = self._format_output(raw_output)

            start_frame = start_indices[i]
            end_frame = start_frame + self.model_params['num_frames']
            start_time_sec = start_frame * self.frame_duration
            end_time_sec = end_frame * self.frame_duration

            block_results.append({
                'block_index': i,
                'start_time': start_time_sec,
                'end_time': end_time_sec,
                'result': result,
                'raw_output': raw_output,
                'normalize_time': normalize_time,
                'inference_time': block_inference_time
            })

        final_result = self._aggregate_results(block_results)
        
        # 计算总时间
        total_time = time.time() - total_start_time
        
        # 如果有最终结果，添加时间信息
        if final_result:
            final_result['preprocess_time'] = preprocess_time
            final_result['inference_time'] = inference_time
            final_result['total_time'] = total_time

        return block_results, final_result

    def _format_output(self, predictions):
        """格式化推理结果"""
        class_idx = np.argmax(predictions)
        confidence = int(predictions[class_idx] * 100)
        # 若没有类别标签，直接返回索引
        label = self.classes[class_idx] if (self.classes and class_idx < len(self.classes)) else f"类别{class_idx}"
        return {
            'class': label,
            'confidence': confidence,
            'probabilities': predictions.tolist()
        }

    def _aggregate_results(self, block_results):
        """聚合所有块的结果"""
        if len(block_results) == 2:
            # 两个块时取置信度最高的
            best_result = max(block_results, key=lambda x: x['result']['confidence'])
            return {
                'class': best_result['result']['class'],
                'confidence': best_result['result']['confidence'],
                'occurrence_percentage': 100.0,
                'total_blocks': len(block_results),
                'class_distribution': {best_result['result']['class']: 1},
                'aggregation_method': 'highest_confidence'
            }

        # 统计每个类别的出现次数和最大置信度
        class_counts = {}
        max_confidence = {}
        for result in block_results:
            cls = result['result']['class']
            conf = result['result']['confidence']
            class_counts[cls] = class_counts.get(cls, 0) + 1
            if cls not in max_confidence or conf > max_confidence[cls]:
                max_confidence[cls] = conf

        if not class_counts:
            return None

        # 多数投票决定最终类别
        most_common_cls = max(class_counts.items(), key=lambda x: x[1])[0]
        count = class_counts[most_common_cls]
        return {
            'class': most_common_cls,
            'confidence': max_confidence[most_common_cls],
            'occurrence_percentage': (count / len(block_results)) * 100,
            'total_blocks': len(block_results),
            'class_distribution': class_counts,
            'aggregation_method': 'majority_vote'
        }

    def release(self):
        """释放RKNN资源"""
        if hasattr(self, 'rknn_lite') and self.rknn_lite:
            self.rknn_lite.release()
            print("RKNN资源已释放")

    def __del__(self):
        """析构函数自动释放资源"""
        self.release()


# 使用示例
if __name__ == "__main__":
    # 加载模型（替换为实际的.rknn模型路径）
    model = Workflow("audio_model.rknn")
    
    # 处理音频文件（替换为实际的音频路径）
    blocks, result = model.inference("test_audio.wav")
    print("\n最终结果:")
    print(f"分类: {result['class']}, 置信度: {result['confidence']}%")
    print(f"在 {result['total_blocks']} 个块中出现比例: {result['occurrence_percentage']:.2f}%")