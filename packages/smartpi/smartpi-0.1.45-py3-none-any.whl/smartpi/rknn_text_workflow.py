import numpy as np
import onnxruntime as ort
import onnx
import json
import os
import time
from transformers import AutoTokenizer
from rknnlite.api import RKNNLite

# 获取当前文件的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 构建默认的GTE模型和分词器配置路径
default_feature_model = os.path.join(current_dir, 'text_gte_model', 'gte', 'gte_model.onnx')
default_tokenizer_path = os.path.join(current_dir, 'text_gte_model', 'config')


class TextClassificationWorkflow:
    def __init__(self, class_model_path, feature_model_path=None, tokenizer_path=None):
        # 如果没有提供路径，则使用默认路径
        self.feature_model_path = feature_model_path or default_feature_model
        self.tokenizer_path = tokenizer_path or default_tokenizer_path
        self.class_model_path = class_model_path
        # 加载分词器
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_path,
            local_files_only=True
        )

        # 加载特征提取模型（保持ONNX不变）
        self.feature_session = ort.InferenceSession(self.feature_model_path)
        self.feature_input_names = [input.name for input in self.feature_session.get_inputs()]

        # 初始化分类模型（替换为RKNN）
        self.class_rknn = RKNNLite()
        self._load_rknn_class_model(class_model_path)
        
        # 加载元数据（类别标签）
        self.label_names = self._load_metadata(class_model_path)
        print(f"分类模型加载成功，共 {len(self.label_names)} 个类别: {self.label_names}")

    def _load_rknn_class_model(self, model_path):
        """加载RKNN分类模型并初始化运行时"""
        try:
            ret = self.class_rknn.load_rknn(model_path)
            if ret != 0:
                raise RuntimeError(f'加载分类RKNN模型失败 ({model_path}), 错误码: {ret}')
            
            ret = self.class_rknn.init_runtime()
            if ret != 0:
                raise RuntimeError(f'初始化分类模型NPU运行时失败, 错误码: {ret}')
                
            print(f"分类RKNN模型加载成功: {os.path.basename(model_path)}")
            
        except Exception as e:
            print(f"分类模型加载失败: {e}")
            raise

    def _get_metadata_path(self, model_path):
        """获取RKNN模型对应的元数据文件路径"""
        base_dir = os.path.dirname(model_path)
        base_name = os.path.basename(model_path)
        metadata_name = os.path.splitext(base_name)[0] + '_metadata.json'
        metadata_path = os.path.join(base_dir, metadata_name)
        
        if not os.path.exists(metadata_path):
            metadata_path = os.path.join(base_dir, 'rknn_metadata.json')
            
        return metadata_path

    def _load_metadata(self, model_path):
        """从RKNN元数据文件加载类别标签"""
        try:
            metadata_path = self._get_metadata_path(model_path)
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                if 'classes' in metadata:
                    return metadata['classes']
                else:
                    print(f"元数据文件中未找到类别信息")

            onnx_model_path = os.path.splitext(model_path)[0] + '.onnx'
            if os.path.exists(onnx_model_path):
                onnx_model = onnx.load(onnx_model_path)
                if onnx_model.metadata_props:
                    for prop in onnx_model.metadata_props:
                        if prop.key == 'classes':
                            try:
                                return json.loads(prop.value)
                            except json.JSONDecodeError:
                                return prop.value.split(',')

        except Exception as e:
            print(f"元数据读取错误: {e}")

        # 获取类别数（修复：确保正确获取输出维度）
        num_classes = 10
        try:
            output_shapes = self.class_rknn.get_output_shape()
            if output_shapes and len(output_shapes) > 0:
                num_classes = output_shapes[0][-1]
        except:
            pass
            
        label_names = [f"Class_{i}" for i in range(num_classes)]
        print(f"警告: 未找到类别信息，使用自动生成的名称: {label_names}")
        return label_names

    def _extract_features(self, texts):
        """特征提取（保持ONNX推理不变）"""
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="np"
        )

        onnx_inputs = {name: inputs[name].astype(np.int64) for name in self.feature_input_names}
        onnx_outputs = self.feature_session.run(None, onnx_inputs)
        last_hidden_state = onnx_outputs[0]
        return last_hidden_state[:, 0, :].astype(np.float32)

    def _classify(self, embeddings):
        """分类推理（修复：支持批量输入，若模型不支持则单样本循环）"""
        embeddings = embeddings.astype(np.float32)
        batch_size = embeddings.shape[0]
        all_results = []

        # 检查RKNN模型是否支持批量输入（通过输入形状判断）
        try:
            input_shapes = self.class_rknn.get_input_shape()
            if input_shapes and len(input_shapes) > 0:
                # 输入形状格式：[batch, ...]，若第一维为-1或大于1则支持批量
                if input_shapes[0][0] in (-1, batch_size):
                    # 支持批量输入，直接推理
                    class_results = self.class_rknn.inference(inputs=[embeddings])[0]
                    return class_results
        except:
            pass

        # 若不支持批量输入，则逐个处理样本
        for i in range(batch_size):
            single_embedding = embeddings[i:i+1]  # 保持维度为[1, feature_dim]
            result = self.class_rknn.inference(inputs=[single_embedding])[0]
            all_results.append(result[0])  # 取单样本结果

        return np.array(all_results)  # 合并为批量结果

    def predict(self, texts):
        """执行文本分类预测，包含时间测量功能"""
        if not texts:
            return [], []

        # 记录总开始时间
        total_start_time = time.time()
        
        # 记录特征提取时间
        feature_start_time = time.time()
        embeddings = self._extract_features(texts)
        feature_time = time.time() - feature_start_time
        
        # 记录分类推理时间
        classify_start_time = time.time()
        probs = self._classify(embeddings)
        classify_time = time.time() - classify_start_time
        
        # 计算总时间
        total_time = time.time() - total_start_time
        
        predicted_indices = np.argmax(probs, axis=1)

        # 打印调试信息：确认批量大小是否正确
        print(f"处理文本数量: {len(texts)}, 预测结果数量: {len(predicted_indices)}")

        raw_results = []
        formatted_results = []

        for i, (text, idx, prob_vec) in enumerate(zip(texts, predicted_indices, probs)):
            label = self.label_names[idx] if idx < len(self.label_names) else f"未知类别 {idx}"
            confidence = float(prob_vec[idx])

            raw_results.append(prob_vec.tolist())
            formatted_results.append({
                'text': text,
                'class': label,
                'confidence': confidence,
                'class_id': int(idx),
                'probabilities': prob_vec.tolist(),
                # 添加时间信息
                'preprocess_time': 0.0,  # 文本不需要传统的图像预处理
                'feature_extract_time': feature_time / len(texts),  # 平均到每个文本
                'inference_time': classify_time / len(texts),  # 平均到每个文本
                'total_time': total_time / len(texts)  # 平均到每个文本
            })

        return raw_results, formatted_results

    def release(self):
        """释放资源"""
        if hasattr(self, 'class_rknn') and self.class_rknn:
            self.class_rknn.release()
        print("RKNN分类模型资源已释放")

    def __del__(self):
        self.release()


# 使用示例
if __name__ == "__main__":
    # 替换为实际路径
    class_model = "./model.rknn"
    
    # 初始化工作流（现在只需要提供分类模型路径，GTE模型和分词器使用默认路径）
    classifier = TextClassificationWorkflow(
        class_model_path=class_model
    )
    
    # 测试文本（2个样本）
    test_texts = [
        "强大",
        "再见"
    ]
    
    # 进行预测
    raw_results, formatted_results = classifier.predict(test_texts)
    
    # 打印所有结果
    print("\n所有预测结果：")
    for i, result in enumerate(formatted_results):
        print(f"样本 {i+1}:")
        print(f"  文本: {result['text']}")
        print(f"  分类: {result['class']}")
        print(f"  置信度: {result['confidence']:.4f}")
        print(f"  类别ID: {result['class_id']}")
        print(f"  概率分布: {result['probabilities']}")
        print("---")
    
    # 释放资源
    classifier.release()