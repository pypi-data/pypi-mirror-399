import numpy as np
import onnxruntime as ort
import onnx
import json
import os
import time
from transformers import AutoTokenizer

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
        # 记录模型初始化开始时间
        init_start_time = time.time()
        
        # 加载分词器
        print("加载分词器...")
        tokenizer_start = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.tokenizer_path,
            local_files_only=True
        )
        tokenizer_time = time.time() - tokenizer_start
        print(f"分词器加载完成，耗时: {tokenizer_time:.3f} 秒")

        # 加载特征提取模型
        print("加载特征提取模型...")
        feature_start = time.time()
        self.feature_session = ort.InferenceSession(self.feature_model_path)
        self.feature_input_names = [input.name for input in self.feature_session.get_inputs()]
        feature_load_time = time.time() - feature_start
        print(f"特征提取模型加载完成，耗时: {feature_load_time:.3f} 秒")

        # 加载分类模型
        print("加载分类模型...")
        class_start = time.time()
        self.class_session = ort.InferenceSession(class_model_path)
        self.class_input_name = self.class_session.get_inputs()[0].name
        self.class_output_name = self.class_session.get_outputs()[0].name
        class_load_time = time.time() - class_start
        print(f"分类模型加载完成，耗时: {class_load_time:.3f} 秒")

        # 加载元数据（类别标签）
        meta_start = time.time()
        self.label_names = self._load_metadata(class_model_path)
        meta_time = time.time() - meta_start
        
        # 计算总初始化时间
        init_total_time = time.time() - init_start_time
        
        print(f"元数据加载完成，耗时: {meta_time:.3f} 秒")
        print(f"分类模型加载成功，共 {len(self.label_names)} 个类别: {self.label_names}")
        print(f"模型初始化总耗时: {init_total_time:.3f} 秒")

    def _load_metadata(self, model_path):
        """从ONNX模型元数据中加载类别标签"""
        try:
            # 使用 ONNX 库加载模型文件
            onnx_model = onnx.load(model_path)

            # 尝试从metadata_props获取
            if onnx_model.metadata_props:
                for prop in onnx_model.metadata_props:
                    if prop.key == 'classes':
                        try:
                            # 尝试解析JSON格式的类别
                            return json.loads(prop.value)
                        except json.JSONDecodeError:
                            # 如果是逗号分隔的字符串
                            return prop.value.split(',')

            # 尝试从doc_string获取
            if onnx_model.doc_string:
                try:
                    doc_dict = json.loads(onnx_model.doc_string)
                    if 'classes' in doc_dict:
                        return doc_dict['classes']
                except:
                    pass
        except Exception as e:
            print(f"元数据读取错误: {e}")

        # 默认值：根据输出形状生成类别名称
        num_classes = self.class_session.get_outputs()[0].shape[-1]
        label_names = [f"Class_{i}" for i in range(num_classes)]
        print(f"警告: 未在模型元数据中找到类别信息，使用自动生成的类别名称: {label_names}")
        return label_names

    def _extract_features(self, texts):
        """对文本进行分词并提取特征向量"""
        # 文本预处理
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="np"
        )

        # 转换输入类型为int64
        onnx_inputs = {name: inputs[name].astype(np.int64) for name in self.feature_input_names}

        # 提取文本特征
        onnx_outputs = self.feature_session.run(None, onnx_inputs)
        last_hidden_state = onnx_outputs[0]
        return last_hidden_state[:, 0, :].astype(np.float32)  # 确保float32类型

    def _classify(self, embeddings):
        """对特征向量进行分类预测"""
        # 分类模型推理
        class_results = self.class_session.run(
            [self.class_output_name],
            {self.class_input_name: embeddings}
        )[0]

        # 应用softmax获取概率分布
        probs = np.exp(class_results) / np.sum(np.exp(class_results), axis=1, keepdims=True)
        return probs

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

        # 格式化结果
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