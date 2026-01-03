import numpy as np
import onnxruntime as ort
import librosa
import onnx
import time
import os


class Workflow:
    def __init__(self, model_path=None, smoothing_time_constant=0, step_size=43):
        self.model = None
        self.classes = []
        self.metadata = {}
        self.model_params = {
            'fft_size': 2048,
            'sample_rate': 44100,
            'num_frames': 43,  # 每块帧数
            'spec_features': 232
        }
        self.global_mean = None
        self.global_std = None
        self.smoothing_time_constant = smoothing_time_constant
        self.step_size = step_size
        self.frame_duration = None
        self.hop_length = 735  # 44100/60=735 (每帧时长 ~16.67ms)
        self.previous_spec = None

        if model_path:
            self.load_model(model_path)

        # 计算帧时间信息
        self.frame_duration = self.hop_length / self.model_params['sample_rate']
        self.block_duration = self.model_params['num_frames'] * self.frame_duration

    def load_model(self, model_path):
        """加载模型并解析元数据"""
        onnx_model = onnx.load(model_path)
        for meta in onnx_model.metadata_props:
            self.metadata[meta.key] = meta.value

        if 'classes' in self.metadata:
            self.classes = eval(self.metadata['classes'])

        if 'global_mean' in self.metadata:
            self.global_mean = np.array(eval(self.metadata['global_mean']))
        if 'global_std' in self.metadata:
            self.global_std = np.array(eval(self.metadata['global_std']))

        self.session = ort.InferenceSession(model_path)
        self.input_shape = self._get_fixed_shape(self.session.get_inputs()[0].shape)

    def _get_fixed_shape(self, shape):
        fixed = []
        for dim in shape:
            if isinstance(dim, str) or dim < 0:
                fixed.append(1)
            else:
                fixed.append(int(dim))
        return fixed

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
        """加载音频文件（支持wav和webm），返回音频数组和采样率"""
        ext = os.path.splitext(audio_path)[1].lower()

        if ext == '.wav':
            # 使用librosa加载wav文件
            audio, sr = librosa.load(audio_path, sr=self.model_params['sample_rate'])
            return audio, sr

        elif ext == '.webm':
            # 使用pydub加载webm文件（需要ffmpeg支持）
            try:
                from pydub import AudioSegment
            except ImportError:
                raise ImportError("处理webm格式需要pydub库，请先安装：pip install pydub")

            try:
                # 加载webm文件
                audio_segment = AudioSegment.from_file(audio_path, format='webm')

                # 转换为单声道
                audio_segment = audio_segment.set_channels(1)

                # 转换采样率
                audio_segment = audio_segment.set_frame_rate(self.model_params['sample_rate'])

                # 转换为numpy数组（范围：[-1, 1]）
                samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                samples = samples / 32768.0  # 16位音频的归一化

                return samples, self.model_params['sample_rate']

            except FileNotFoundError as e:
                if 'ffmpeg' in str(e).lower() or 'avconv' in str(e).lower():
                    print("\n" + "="*60)
                    print("检测到错误：缺少ffmpeg支持，无法处理webm格式音频")
                    print("="*60)
                    print("ffmpeg是处理webm等音频格式的必要工具，请按照以下教程安装：\n")

                    print("【Linux系统安装教程】")
                    print("1. Ubuntu/Debian系统：")
                    print("   sudo apt update")
                    print("   sudo apt install ffmpeg\n")

                    print("2. CentOS/RHEL系统：")
                    print("   sudo yum install epel-release")
                    print("   sudo yum install ffmpeg ffmpeg-devel\n")

                    print("3. Fedora系统：")
                    print("   sudo dnf install ffmpeg\n")

                    print("4. Arch Linux系统：")
                    print("   sudo pacman -S ffmpeg\n")

                    print("【Windows系统安装教程】")
                    print("1. 访问ffmpeg官网下载页：https://ffmpeg.org/download.html#build-windows")
                    print("2. 推荐下载方式：")
                    print("   - 从 Gyan.dev 下载：https://www.gyan.dev/ffmpeg/builds/")
                    print("   - 选择 'ffmpeg-release-essentials.zip' 版本")
                    print("3. 解压下载的zip文件到任意目录（例如：C:\\ffmpeg）")
                    print("4. 配置环境变量：")
                    print("   - 右键点击'此电脑' -> '属性' -> '高级系统设置' -> '环境变量'")
                    print("   - 在'系统变量'中找到'Path'，点击'编辑'")
                    print("   - 点击'新建'，添加ffmpeg的bin目录路径（例如：C:\\ffmpeg\\bin）")
                    print("   - 点击所有窗口的'确定'保存设置")
                    print("5. 验证安装：打开新的命令提示符，输入 'ffmpeg -version'，能显示版本信息即为安装成功\n")

                    print("安装完成后，请重新运行程序。")
                    print("="*60 + "\n")
                    raise  # 重新抛出异常终止程序
                else:
                    raise  # 其他文件未找到错误，正常抛出
            except Exception as e:
                print(f"处理webm音频时发生其他错误：{str(e)}")
                raise

        else:
            raise ValueError(f"不支持的音频格式: {ext}，目前支持 .wav 和 .webm")

    def _preprocess_audio(self, audio_path):
        """预处理整个音频文件，返回分贝谱"""
        audio, sr = self._load_audio(audio_path)
        assert sr == self.model_params['sample_rate'], f"采样率不匹配，需要 {self.model_params['sample_rate']}Hz"

        # 使用新参数计算STFT
        hop_length = self.hop_length
        win_length = self.model_params['fft_size']
        n_fft = self.model_params['fft_size']

        # 手动分帧并加窗
        frames = librosa.util.frame(audio, frame_length=win_length, hop_length=hop_length)
        windowed_frames = np.zeros_like(frames)
        for i in range(frames.shape[1]):
            windowed_frames[:, i] = self._apply_hann_window(frames[:, i])

        # 执行FFT
        D = np.fft.rfft(windowed_frames, n=n_fft, axis=0)

        # 计算幅度谱并转分贝
        magnitude = np.abs(D)
        db = 20 * np.log10(np.maximum(1e-5, magnitude))

        # 截取需要的特征维度并转置
        db = db[:self.model_params['spec_features'], :]
        spec = db.T  # 转置为[时间帧, 频率特征]

        return spec
    
    def preprocess_audio_segment(self, audio_segment):
        """预处理音频片段（用于实时处理），返回分贝谱"""
        # 确保音频是单声道且采样率正确
        sr = self.model_params['sample_rate']
        
        # 使用新参数计算STFT
        hop_length = self.hop_length
        win_length = self.model_params['fft_size']
        n_fft = self.model_params['fft_size']

        # 手动分帧并加窗
        frames = librosa.util.frame(audio_segment, frame_length=win_length, hop_length=hop_length)
        windowed_frames = np.zeros_like(frames)
        for i in range(frames.shape[1]):
            windowed_frames[:, i] = self._apply_hann_window(frames[:, i])

        # 执行FFT
        D = np.fft.rfft(windowed_frames, n=n_fft, axis=0)

        # 计算幅度谱并转分贝
        magnitude = np.abs(D)
        db = 20 * np.log10(np.maximum(1e-5, magnitude))

        # 截取需要的特征维度并转置
        db = db[:self.model_params['spec_features'], :]
        spec = db.T  # 转置为[时间帧, 频率特征]

        return spec

    def _extract_blocks(self, full_spec):
        """从完整频谱中提取指定帧数的块"""
        total_frames = full_spec.shape[0]
        blocks = []
        start_indices = []

        num_blocks = (total_frames - self.model_params['num_frames']) // self.step_size + 1

        for i in range(num_blocks):
            start = i * self.step_size
            end = start + self.model_params['num_frames']

            block = full_spec[start:end, :]

            if block.shape[0] < self.model_params['num_frames']:
                padded = np.zeros((self.model_params['num_frames'], self.model_params['spec_features']))
                padded[:block.shape[0]] = block
                block = padded

            blocks.append(block)
            start_indices.append(start)

        return blocks, start_indices

    def _normalize(self, spec):
        """归一化处理"""
        epsilon = 1e-8
        mean = np.mean(spec)
        variance = np.var(spec)
        std = np.sqrt(variance)
        normalized = (spec - mean) / (std + epsilon)
        return normalized.astype(np.float32)

    def inference(self, audio_path, model_path=None):
        if model_path and not hasattr(self, 'session'):
            self.load_model(model_path)

        full_spec = self._preprocess_audio(audio_path)
        blocks, start_indices = self._extract_blocks(full_spec)

        block_results = []

        print(f"开始处理音频: {audio_path}")
        print(f"总帧数: {full_spec.shape[0]}, 总时长: {full_spec.shape[0] * self.frame_duration:.2f}秒")
        print(f"将处理 {len(blocks)} 个块 (每块 {self.model_params['num_frames']}帧 = {self.block_duration:.3f}秒)")
        print("=" * 60)

        for i, block in enumerate(blocks):
            start_time = time.time()

            normalized_block = self._normalize(block)
            input_tensor = normalized_block.flatten().reshape(self.input_shape)

            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: input_tensor})

            raw_output = outputs[0][0]
            result = self._format_output(raw_output)

            process_time = time.time() - start_time
            start_frame = start_indices[i]
            end_frame = start_frame + self.model_params['num_frames']
            start_time_sec = start_frame * self.frame_duration
            end_time_sec = end_frame * self.frame_duration

            block_result = {
                'block_index': i,
                'start_frame': start_frame,
                'end_frame': end_frame,
                'start_time': start_time_sec,
                'end_time': end_time_sec,
                'process_time': process_time,
                'result': result,
                'raw_output': raw_output
            }

            block_results.append(block_result)

            print(f"块 #{i+1} [时间: {start_time_sec:.2f}-{end_time_sec:.2f}s]")
            print(f"  分类: {result['class']}, 置信度: {result['confidence']}%")
            print(f"  处理时间: {process_time * 1000:.2f}ms")
            print("-" * 50)

        final_result = self._aggregate_results(block_results)
        return block_results, final_result
        
    def process_audio_segment(self, audio_segment):
        """处理音频片段（用于实时处理），包含时间测量功能"""
        if not hasattr(self, 'session'):
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
            input_tensor = normalized_block.flatten().reshape(self.input_shape)
            normalize_time = time.time() - normalize_start_time
            
            # 记录推理时间
            inference_start_time = time.time()
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: input_tensor})
            block_inference_time = time.time() - inference_start_time
            inference_time += block_inference_time

            raw_output = outputs[0][0]
            result = self._format_output(raw_output)

            start_frame = start_indices[i]
            end_frame = start_frame + self.model_params['num_frames']
            start_time_sec = start_frame * self.frame_duration
            end_time_sec = end_frame * self.frame_duration

            block_result = {
                'block_index': i,
                'start_frame': start_frame,
                'end_frame': end_frame,
                'start_time': start_time_sec,
                'end_time': end_time_sec,
                'result': result,
                'raw_output': raw_output,
                'normalize_time': normalize_time,
                'inference_time': block_inference_time
            }

            block_results.append(block_result)

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
        class_idx = np.argmax(predictions)
        confidence = int(predictions[class_idx] * 100)
        if len(self.classes) > 0:
            label = self.classes[class_idx] if class_idx < len(self.classes) else "未知"
        else:
            label = str(class_idx)
        return {
            'class': label,
            'confidence': confidence,
            'probabilities': predictions.tolist()
        }

    def _aggregate_results(self, block_results):
        """聚合所有块的结果"""
        if len(block_results) == 2:
            # 两个块时取置信度最高的
            max_confidence = -1
            best_result = None
            for result in block_results:
                if result['result']['confidence'] > max_confidence:
                    max_confidence = result['result']['confidence']
                    best_result = result
            return {
                'class': best_result['result']['class'],
                'confidence': best_result['result']['confidence'],
                'occurrence_percentage': 100.0,
                'total_blocks': len(block_results),
                'best_raw_output': best_result['raw_output'],
                'class_distribution': {best_result['result']['class']: 1},
                'aggregation_method': 'highest_confidence'
            }

        # 正常情况：统计每个类别的出现次数
        class_counts = {}
        max_confidence = {}

        for result in block_results:
            class_label = result['result']['class']
            confidence = result['result']['confidence']

            class_counts[class_label] = class_counts.get(class_label, 0) + 1
            if class_label not in max_confidence or confidence > max_confidence[class_label]:
                max_confidence[class_label] = confidence

        if not class_counts:
            return None

        # 找出最频繁的类别
        most_common = max(class_counts.items(), key=lambda x: x[1])
        most_common_class = most_common[0]
        count = most_common[1]
        percentage = (count / len(block_results)) * 100
        confidence = max_confidence[most_common_class]

        # 找出该类别中置信度最高的原始输出
        best_raw_output = None
        for result in block_results:
            if result['result']['class'] == most_common_class:
                if best_raw_output is None or result['result']['confidence'] > best_raw_output['result']['confidence']:
                    best_raw_output = result

        return {
            'class': most_common_class,
            'confidence': confidence,
            'occurrence_percentage': percentage,
            'total_blocks': len(block_results),
            'best_raw_output': best_raw_output['raw_output'] if best_raw_output else None,
            'class_distribution': class_counts,
            'aggregation_method': 'majority_vote'
        }
    