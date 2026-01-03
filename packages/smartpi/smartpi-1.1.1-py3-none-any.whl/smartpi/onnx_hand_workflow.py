import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp
import json
from PIL import Image
import time  # 用于时间测量

class GestureWorkflow:
    def __init__(self, model_path):
        # 初始化MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,  # 视频流模式  如果只是获取照片的手势关键点 请设置为True
            max_num_hands=1,#如果想要检测双手，请设置成2
            min_detection_confidence=0.5,#手势关键点的阈值
            model_complexity=0#使用最简单的模型  如果效果不准确 可以考虑设置比较复制的模型  1
        )
        
        # 初始化元数据
        self.min_vals = None
        self.max_vals = None
        self.class_labels = None
        
        # 加载模型和元数据
        self.load_model(model_path)
    
    def load_model(self, model_path):
        """加载模型并解析元数据"""
        # 初始化ONNX Runtime会话
        self.session = ort.InferenceSession(model_path)
        
        # 加载元数据
        self._load_metadata()
    
    def _load_metadata(self):
        """从ONNX模型元数据中加载归一化参数和类别标签"""
        model_meta = self.session.get_modelmeta()
        
        # 检查custom_metadata_map是否存在
        if hasattr(model_meta, 'custom_metadata_map'):
            metadata = model_meta.custom_metadata_map
            if 'minMaxValues' in metadata:
                min_max_data = json.loads(metadata['minMaxValues'])
                self.min_vals = min_max_data.get('min')
                self.max_vals = min_max_data.get('max')
            
            if 'classes' in metadata:
                class_labels = json.loads(metadata['classes'])
                self.class_labels = list(class_labels.values()) if isinstance(class_labels, dict) else class_labels
        else:
            # 对于旧版本的ONNX Runtime，使用metadata_props
            for prop in model_meta.metadata_props:
                if prop.key == 'minMaxValues':
                    min_max_data = json.loads(prop.value)
                    self.min_vals = min_max_data.get('min')
                    self.max_vals = min_max_data.get('max')
                elif prop.key == 'classes':
                    class_labels = json.loads(prop.value)
                    self.class_labels = list(class_labels.values()) if isinstance(class_labels, dict) else class_labels
        
        # 设置默认值
        if self.class_labels is None:
            self.class_labels = ["点赞", "点踩", "胜利", "拳头", "我爱你", "手掌"]
    
    def preprocess_image(self, image, target_width=224, target_height=224):
        """
        预处理图像：保持比例缩放并居中放置在目标尺寸的画布上
        返回处理后的OpenCV图像 (BGR格式)
        """
        # 将OpenCV图像转换为PIL格式
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # 计算缩放比例
        width, height = pil_image.size
        scale = min(target_width / width, target_height / height)
        
        # 计算新尺寸和位置
        new_width = int(width * scale)
        new_height = int(height * scale)
        x = (target_width - new_width) // 2
        y = (target_height - new_height) // 2
        
        # 创建白色背景画布并粘贴缩放后的图像
        canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
        resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        canvas.paste(resized_image, (x, y))
        
        # 转换回OpenCV格式
        processed_image = np.array(canvas)
        return cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR)
    
    def extract_hand_keypoints(self, image):
        """从图像中提取手部关键点"""
        # 转换图像为RGB格式并处理
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
            # 只使用检测到的第一只手
            landmarks = results.multi_hand_world_landmarks[0]
            
            # 提取关键点坐标
            keypoints = []
            for landmark in landmarks.landmark:
                keypoints.extend([landmark.x, landmark.y, landmark.z])
                
            return np.array(keypoints, dtype=np.float32)
        return None
    
    def normalize_keypoints(self, keypoints):
        """归一化关键点数据"""
        if self.min_vals is None or self.max_vals is None:
            return keypoints  # 如果没有归一化参数，返回原始数据
            
        normalized = []
        for i, value in enumerate(keypoints):
            if i < len(self.min_vals) and i < len(self.max_vals):
                min_val = self.min_vals[i]
                max_val = self.max_vals[i]
                if max_val - min_val > 0:
                    normalized.append((value - min_val) / (max_val - min_val))
                else:
                    normalized.append(0)
            else:
                normalized.append(value)
        
        return np.array(normalized, dtype=np.float32)
    
    def predict_frame(self, frame):
        """执行手势分类预测（直接处理图像帧）"""
        # 记录开始时间
        start_time = time.time()
        # 预处理图像
        processed_image = self.preprocess_image(frame, 224, 224)
        
        # 提取关键点
        keypoints = self.extract_hand_keypoints(processed_image)
        min_time = time.time()
        hand_time = min_time - start_time      
        #print(f"关键点识别耗时: {hand_time:.4f}秒")
        if keypoints is None:
            return None, {"error": "未检测到手部"}
        
        # 归一化关键点
        normalized_kps = self.normalize_keypoints(keypoints)
        
        # 准备ONNX输入
        input_data = normalized_kps.reshape(1, -1).astype(np.float32)
        
        # 运行推理
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_data})
        predictions = outputs[0][0]
        
        # 获取预测结果
        class_id = np.argmax(predictions)
        confidence = float(predictions[class_id])
        
        # 获取类别标签
        label = self.class_labels[class_id] if class_id < len(self.class_labels) else f"未知类别 {class_id}"
        end_time = time.time()
        all_time = end_time - start_time      
        onnx_time = end_time - min_time   
        print(f"onnx耗时: {onnx_time:.4f}秒")
        print(f"总耗时: {all_time:.4f}秒")
        # 返回原始结果和格式化结果
        raw_result = predictions.tolist()
        formatted_result = {
            'class': label,
            'confidence': confidence,
            'class_id': class_id,
            'probabilities': raw_result
        }
        
        return raw_result, formatted_result

    # 保留原始方法以兼容旧代码
    def predict(self, image_path):
        """执行手势分类预测（从文件路径）"""
        try:
            # 使用PIL库读取图像，避免libpng版本问题
            pil_image = Image.open(image_path)
            # 转换为RGB格式
            rgb_image = pil_image.convert('RGB')
            # 转换为numpy数组
            image_array = np.array(rgb_image)
            # 转换为BGR格式（OpenCV使用的格式）
            image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            
            return self.predict_frame(image)
        except Exception as e:
            # 如果PIL失败，尝试使用cv2作为备选
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")
            return self.predict_frame(image)