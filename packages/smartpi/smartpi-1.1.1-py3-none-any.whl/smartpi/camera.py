# coding: utf-8
import cv2
import os
import time
import platform

class Camera:
    def __init__(self, indexes=[0, 1, 2, 3], target_width=640, target_height=480):
        self.cap = None
        self.indexes = indexes
        self.target_width = target_width
        self.target_height = target_height
        self.open_camera()
    
    def open_camera(self):
        """打开摄像头（硬件加速+参数优化）"""
        for idx in self.indexes:
            try:
                # 适配linux/Android的V4L2硬件加速（RK芯片优先）
                if platform.system() == "Linux":
                    cap = cv2.VideoCapture(idx, cv2.CAP_V4L2)
                    # 尝试启用硬件加速（兼容不同OpenCV版本）
                    try:
                        # 对于较新版本的OpenCV
                        if hasattr(cv2, 'CAP_PROP_HW_ACCELERATION') and hasattr(cv2, 'VIDEO_ACCELERATION_ANY'):
                            cap.set(cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)
                    except AttributeError as ae:
                        print(f"硬件加速设置不支持，使用默认配置: {ae}")
                else:
                    cap = cv2.VideoCapture(idx)
                
                if cap.isOpened():
                    # 尝试设置分辨率
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.target_width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.target_height)
                    
                    # 获取实际设置的分辨率
                    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    print(f"摄像头 {idx} 已打开, 分辨率: {actual_width}x{actual_height}")
                    self.cap = cap
                    return True
            except Exception as e:
                print(f"尝试打开摄像头 {idx} 失败: {e}")
                continue
        
        print("无法打开任何摄像头")
        return False
    
    def read_frame(self):
        """读取一帧并自动处理错误"""
        if not self.cap or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        if not ret:
            print("读取帧失败，尝试重新打开摄像头...")
            self.release()
            time.sleep(1)
            if self.open_camera():
                return self.read_frame()
            return False, None
        
        # 调整到目标分辨率
        if frame.shape[1] != self.target_width or frame.shape[0] != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height))
            
        return True, frame
    
    def get_resolution(self):
        """获取当前分辨率"""
        if self.cap and self.cap.isOpened():
            return (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )
        return self.target_width, self.target_height
    
    def release(self):
        """释放摄像头资源"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None