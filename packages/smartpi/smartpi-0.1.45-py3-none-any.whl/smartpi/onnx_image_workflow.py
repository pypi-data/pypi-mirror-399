import onnxruntime as ort
import numpy as np
from PIL import Image
import onnx
import cv2
import time

class ImageWorkflow:
    def __init__(self, model_path=None):
        self.session = None
        self.classes = []
        self.metadata = {}
        self.input_shape = [1, 224, 224, 3]  # 默认输入形状
        
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        """加载模型并解析元数据"""
        try:
            # 读取ONNX元数据
            onnx_model = onnx.load(model_path)
            for meta in onnx_model.metadata_props:
                self.metadata[meta.key] = meta.value
            
            # 解析类别标签
            if 'classes' in self.metadata:
                self.classes = eval(self.metadata['classes'])
            
            # 初始化推理会话
            self.session = ort.InferenceSession(model_path)
            self._parse_input_shape()
            
        except Exception as e:
            print(f"模型加载失败: {e}")

    def _parse_input_shape(self):
        """自动解析输入形状"""
        input_info = self.session.get_inputs()[0]
        shape = []
        for dim in input_info.shape:
            # 处理动态维度（用1替代）
            shape.append(1 if isinstance(dim, str) or dim < 0 else int(dim))
        self.input_shape = shape

    def _preprocess(self, image_path):
        """标准化预处理流程"""
        try:
            img = Image.open(image_path).convert("RGB")
            
            # 获取目标尺寸（假设形状为 [N, H, W, C]）
            _, target_h, target_w, _ = self.input_shape
            
            # 调整尺寸
            img = img.resize((target_w, target_h), Image.BILINEAR)
            
            # 转换为numpy数组并归一化
            img_array = np.array(img).astype(np.float32) / 255.0
            
            # 添加batch维度
            return np.expand_dims(img_array, axis=0)
            
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return None

    def inference(self, data, model_path=None):
        """执行推理"""
        if model_path and not self.session:
            self.load_model(model_path)
        
        input_data = self._preprocess(data)
        if input_data is None:
            return None, None
        
        try:
            # 运行推理
            outputs = self.session.run(None, {self.session.get_inputs()[0].name: input_data})
            raw = outputs[0][0]  # 假设输出形状为 [1, n_classes]
            
            # 格式化输出
            formatted = self._format_result(raw)
            
            return raw, formatted
        
        except Exception as e:
            print(f"推理失败: {e}")
            return None, None

    def inference_frame(self, frame_data, model_path=None):
        """直接使用帧数据进行推理，无需文件IO
        返回值：raw, formatted
        formatted字典包含：class, confidence, probabilities, preprocess_time, inference_time
        """
        if model_path and not self.session:
            self.load_model(model_path)
        
        # 测量预处理时间
        preprocess_start = time.time()
        input_data = self._preprocess_frame(frame_data)
        preprocess_time = time.time() - preprocess_start
        
        if input_data is None:
            return None, None
        
        try:
            # 测量推理时间
            inference_start = time.time()
            # 运行推理
            outputs = self.session.run(None, {self.session.get_inputs()[0].name: input_data})
            inference_time = time.time() - inference_start
            
            raw = outputs[0][0]  # 假设输出形状为 [1, n_classes]
            
            # 格式化输出
            formatted = self._format_result(raw)
            # 添加时间信息到返回结果
            formatted['preprocess_time'] = preprocess_time
            formatted['inference_time'] = inference_time
            
            # 计算总耗时
            total_time = preprocess_time + inference_time
            print(f"帧推理耗时: {total_time:.4f}秒 - 识别结果: {formatted['class']} ({formatted['confidence']}%)")
            return raw, formatted
        
        except Exception as e:
            print(f"帧数据推理失败: {e}")
            return None, None

    def _preprocess_frame(self, frame_data):
        """处理帧数据的预处理流程"""
        try:
            # 确保输入是numpy数组
            if not isinstance(frame_data, np.ndarray):
                print("错误: 帧数据必须是numpy数组")
                return None
                
            # OpenCV读取的帧是BGR格式，转换为RGB
            img = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)
            
            # 获取目标尺寸（假设形状为 [N, H, W, C]）
            _, target_h, target_w, _ = self.input_shape
            
            # 调整尺寸
            img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            
            # 转换为numpy数组并归一化
            img_array = img.astype(np.float32) / 255.0
            
            # 添加batch维度
            return np.expand_dims(img_array, axis=0)
            
        except Exception as e:
            print(f"帧数据预处理失败: {e}")
            return None

    def _format_result(self, predictions):
        """生成标准化输出"""
        class_idx = np.argmax(predictions)
        confidence = int(predictions[class_idx] * 100)
        
        return {
            'class': self.classes[class_idx] if self.classes else str(class_idx),
            'confidence': confidence,
            'probabilities': predictions.tolist()
        }

# 使用示例
if __name__ == "__main__":
    # 预加载模型
    model = ImageWorkflow("model.onnx")
    
    # 使用帧数据进行推理
    # 假设frame是通过cv2获取的帧
    # raw, res = model.inference_frame(frame)
    # print(f"识别结果: {res['class']} ({res['confidence']}%)")
