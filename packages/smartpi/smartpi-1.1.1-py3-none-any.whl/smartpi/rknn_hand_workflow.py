import cv2
import numpy as np
import mediapipe as mp
import json
from PIL import Image
import os
from rknnlite.api import RKNNLite  # 导入RKNNLite
import time  # 用于时间测量

class GestureWorkflow:
    def __init__(self, model_path):
        # 确保model_path是绝对路径
        self.model_path = os.path.abspath(model_path)
        
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
        self.load_model(self.model_path)
    
    def load_model(self, model_path):
        """加载RKNN模型并解析元数据"""
        # 创建RKNNLite实例
        self.rknn_lite = RKNNLite()
        
        # 加载RKNN模型
        ret = self.rknn_lite.load_rknn(model_path)
        if ret != 0:
            raise RuntimeError(f'加载RKNN模型失败, 错误码: {ret}')
        
        # 初始化运行时环境  强制使用npu  core_mask=RKNNLite.NPU_CORE_0
        ret = self.rknn_lite.init_runtime()
        if ret != 0:
            raise RuntimeError(f'初始化NPU运行时失败, 错误码: {ret}')
        
        # 从同目录的JSON文件加载元数据
        metadata_path = self._get_metadata_path(model_path)
        self._load_metadata(metadata_path)
    
    def _get_metadata_path(self, model_path):
        """获取元数据文件的绝对路径"""
        # 尝试与模型同目录的JSON文件
        base_dir = os.path.dirname(model_path)
        base_name = os.path.basename(model_path)
        metadata_name = os.path.splitext(base_name)[0] + 'rknn_metadata.json'
        metadata_path = os.path.join(base_dir, metadata_name)
        
        # 如果文件不存在，尝试默认名称
        if not os.path.exists(metadata_path):
            metadata_path = os.path.join(base_dir, 'rknn_metadata.json')
            
        return metadata_path
    
    def _load_metadata(self, metadata_path):
        """从JSON文件加载元数据"""
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            self.class_labels = metadata.get('classes', ["点赞", "点踩", "胜利", "拳头", "我爱你", "手掌"])
            min_max = metadata.get('minMax', {})
            self.min_vals = min_max.get('min', [])
            self.max_vals = min_max.get('max', [])
            
            print(f"从 {metadata_path} 加载元数据成功")
            print(f"类别标签: {self.class_labels}")
            
        except Exception as e:
            print(f"加载元数据失败: {e}")
            # 设置默认值
            self.class_labels = ["点赞", "点踩", "胜利", "拳头", "我爱你", "手掌"]
            self.min_vals = []
            self.max_vals = []
    
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
        if not self.min_vals or not self.max_vals or len(self.min_vals) != len(keypoints):
            # 如果没有归一化参数或长度不匹配，返回原始数据
            return keypoints
            
        normalized = []
        for i, value in enumerate(keypoints):
            min_val = self.min_vals[i]
            max_val = self.max_vals[i]
            if max_val - min_val > 1e-6:  # 避免除以零
                normalized.append((value - min_val) / (max_val - min_val))
            else:
                normalized.append(0.0)
        
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
            # 记录结束时间并计算耗时
            end_time = time.time()
            #print(f"识别耗时: {end_time - start_time:.4f}秒 (未检测到手部)")
            return None, {"error": "未检测到手部", "processing_time": end_time - start_time}
        
        # 归一化关键点
        normalized_kps = self.normalize_keypoints(keypoints)
        
        # 准备输入数据 (1, 63) 形状
        input_data = normalized_kps.reshape(1, -1).astype(np.float32)
        
        # 使用RKNN Lite进行推理
        try:
            outputs = self.rknn_lite.inference(inputs=[input_data])
            predictions = outputs[0][0]
            
            # 获取预测结果
            class_id = np.argmax(predictions)
            confidence = float(predictions[class_id])
            
            # 获取类别标签
            label = self.class_labels[class_id] if class_id < len(self.class_labels) else f"未知类别 {class_id}"
            
            # 返回原始结果和格式化结果
            raw_result = predictions.tolist()
            formatted_result = {
                'class': label,
                'confidence': confidence,
                'class_id': class_id,
                'probabilities': raw_result
            }
            
            # 记录结束时间并计算耗时
            end_time = time.time()
            rknn_time= end_time - min_time  
            processing_time  = end_time - start_time   
            print(f"rknn识别耗时: {rknn_time:.4f}秒") 
            print(f"总共识别耗时: {processing_time:.4f}秒 - 识别结果: {label} (置信度: {confidence:.2f})")
            
            return raw_result, formatted_result
            
        except Exception as e:
            # 记录结束时间并计算耗时
            end_time = time.time()
            print(f"推理失败: {e}, 耗时: {end_time - start_time:.4f}秒")
            return None, {"error": f"推理失败: {str(e)}", "processing_time": end_time - start_time}
    
    def release(self):
        """释放资源"""
        if hasattr(self, 'rknn_lite'):
            self.rknn_lite.release()
            print("NPU资源已释放")
    
    def __del__(self):
        """析构函数自动释放资源"""
        self.release()

    # 保留原始方法以兼容旧代码
    def predict(self, image_path):
        """执行手势分类预测（从文件路径）"""
        # 确保图像路径是绝对路径
        absolute_image_path = os.path.abspath(image_path)
        
        try:
            # 使用PIL库读取图像，避免libpng版本问题
            pil_image = Image.open(absolute_image_path)
            # 转换为RGB格式
            rgb_image = pil_image.convert('RGB')
            # 转换为numpy数组
            image_array = np.array(rgb_image)
            # 转换为BGR格式（OpenCV使用的格式）
            image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            if image is None:
                raise ValueError(f"无法读取图像: {absolute_image_path}")
            
            return self.predict_frame(image)
        except Exception as e:
            # 如果PIL失败，尝试使用cv2作为备选
            image = cv2.imread(absolute_image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {absolute_image_path}")
            return self.predict_frame(image)