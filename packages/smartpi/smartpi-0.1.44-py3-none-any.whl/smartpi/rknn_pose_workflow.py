import cv2
import numpy as np
from PIL import Image
import json
import os
import time
from rknnlite.api import RKNNLite  # RKNN核心库
from posenet_utils import get_posenet_output  # 姿态关键点提取逻辑（需支持返回3个值）


class PoseWorkflow:
    def __init__(self, model_path=None):
        # 基础属性初始化
        self.model_path = os.path.abspath(model_path) if model_path else None
        self.rknn_lite = None  # RKNN Lite实例
        self.classes = []  # 姿态类别标签
        self.input_shape = []  # 模型输入形状
        self.output_shape = []  # 模型输出形状
        self.min_vals = None  # 归一化用最小值
        self.max_vals = None  # 归一化用最大值
        
        # 新增：有效关键点校验配置（可根据需求调整阈值）
        self.min_valid_keypoints = 1  # 最小有效关键点数量（低于此值则推理终止）
        
        # 结果相关属性
        self.result_image_path = "result.jpg"
        self.processed_image = None
        self.last_infer_time = 0.0  # 记录上一帧推理耗时（用于FPS计算）

        # 若传入模型路径，直接加载
        if model_path:
            self.load_model()

    def _get_metadata_path(self):
        """获取元数据文件路径"""
        if not self.model_path:
            raise ValueError("模型路径未初始化")
        
        # 元数据文件规则：与模型同目录，模型名+"_rknn_metadata.json"
        base_dir = os.path.dirname(self.model_path)
        base_name = os.path.basename(self.model_path)
        metadata_name = os.path.splitext(base_name)[0] + "_rknn_metadata.json"
        metadata_path = os.path.join(base_dir, metadata_name)
        
        # 若自定义名不存在，尝试默认名
        if not os.path.exists(metadata_path):
            metadata_path = os.path.join(base_dir, "rknn_metadata.json")
            print(f"自定义元数据文件不存在，尝试默认路径：{metadata_path}")
        
        return metadata_path

    def _load_metadata(self):
        """加载元数据（classes、input_shape、minMax等）"""
        metadata_path = self._get_metadata_path()
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # 读取核心元数据
            self.classes = metadata.get("classes", [])  # 姿态类别列表
            self.input_shape = [1, 14739]  # 输入形状，默认14739维
            self.output_shape = metadata.get("output_shape", [1, len(self.classes)])  # 输出形状
            min_max = metadata.get("minMax", {})
            self.min_vals = np.array(min_max.get("min", []), dtype=np.float32)  # 归一化最小值
            self.max_vals = np.array(min_max.get("max", []), dtype=np.float32)  # 归一化最大值
            
        
        except Exception as e:
            print(f"元数据加载失败：{e}，使用默认配置")
            self.classes = []
            self.input_shape = [1, 14739] 
            self.min_vals = np.array([])
            self.max_vals = np.array([])

    def load_model(self):
        """加载RKNN模型"""
        try:
            # 初始化RKNN Lite
            self.rknn_lite = RKNNLite()
            
            # 加载RKNN模型文件
            ret = self.rknn_lite.load_rknn(self.model_path)
            if ret != 0:
                raise RuntimeError(f"RKNN模型加载失败，错误码：{ret}")
            
            # 初始化NPU运行时
            ret = self.rknn_lite.init_runtime()
            if ret != 0:
                raise RuntimeError(f"NPU运行时初始化失败，错误码：{ret}")
            
            # 加载元数据
            self._load_metadata()
            print("RKNN模型加载完成")
        
        except Exception as e:
            print(f"模型加载总失败：{e}")
            # 释放资源避免泄漏
            if self.rknn_lite:
                self.rknn_lite.release()

    def _normalize_pose_points(self, pose_points):
        """姿态关键点归一化"""
        pose_points = np.array(pose_points, dtype=np.float32)
        # 若元数据有minMax且长度匹配，使用minMax归一化
        if len(self.min_vals) > 0 and len(self.max_vals) > 0 and len(self.min_vals) == len(pose_points):
            # 避免除以零
            ranges = self.max_vals - self.min_vals
            ranges[ranges < 1e-6] = 1e-6
            normalized = (pose_points - self.min_vals) / ranges
            return normalized
        return pose_points

    def _preprocess(self, pose_data):
        """姿态数据预处理"""
        try:
            # 转为numpy数组
            if not isinstance(pose_data, np.ndarray):
                pose_data = np.array(pose_data, dtype=np.float32)
            
            # 归一化
            normalized_data = self._normalize_pose_points(pose_data)
            
            # 调整为模型输入形状
            input_size = np.prod(self.input_shape)
            if normalized_data.size != input_size:
                print(f"输入数据长度不匹配（实际：{normalized_data.size} | 期望：{input_size}），自动调整维度")
                normalized_data = np.resize(normalized_data, self.input_shape)
            else:
                normalized_data = normalized_data.reshape(self.input_shape)
            
            # RKNN要求输入为float32
            return normalized_data.astype(np.float32)
        
        except Exception as e:
            print(f"姿态数据预处理失败：{e}")
            return None

    def _get_pose_from_image(self, image_path):
        """从图像提取姿态数据（含耗时统计+有效关键点计数）"""
        try:
            print(f"正在处理图像：{image_path}")
            # 记录姿态提取开始时间
            pose_extract_start = time.time()
            
            # 图像读取与预处理
            img = Image.open(image_path).convert("RGB")
            target_h, target_w = 257, 257  # PoseNet默认输入尺寸
            img_resized = img.resize((target_w, target_h), Image.BILINEAR)
            self.processed_image = np.array(img_resized, dtype=np.uint8)
            
            # 【关键修改1】调用PoseNet获取3个返回值：姿态数据、是否有姿态、有效关键点数量
            pose_data, has_pose, valid_keypoint_count = get_posenet_output(image_path)
            # 处理可能的None值（避免后续报错）
            valid_keypoint_count = valid_keypoint_count if valid_keypoint_count is not None else 0
            
            # 【关键校验1】有效关键点数量不足，返回无效结果
            if valid_keypoint_count < self.min_valid_keypoints:
                pose_extract_time = time.time() - pose_extract_start
                print(f"图像有效关键点不足（{valid_keypoint_count}/{self.min_valid_keypoints}），无法提取姿态")
                return None, pose_extract_time, valid_keypoint_count
            
            # 姿态数据为空的情况
            if pose_data is None or not has_pose:
                pose_extract_time = time.time() - pose_extract_start
                print(f"无法从图像中获取姿态数据 | 姿态提取耗时：{pose_extract_time:.4f}s")
                return None, pose_extract_time, valid_keypoint_count
            
            # 姿态数据格式转换
            pose_array = self._parse_pose_data(pose_data)
            # 计算姿态提取耗时
            pose_extract_time = time.time() - pose_extract_start
            print(f"图像姿态提取完成 | 有效关键点：{valid_keypoint_count}/{self.min_valid_keypoints} | 姿态提取耗时：{pose_extract_time:.4f}s")
            return pose_array, pose_extract_time, valid_keypoint_count
        
        except Exception as e:
            pose_extract_time = time.time() - pose_extract_start
            valid_keypoint_count = 0  # 异常时默认关键点数量为0
            print(f"获取图像姿态数据失败：{e} | 姿态提取耗时：{pose_extract_time:.4f}s | 有效关键点：{valid_keypoint_count}")
            return None, pose_extract_time, valid_keypoint_count

    def _parse_pose_data(self, pose_data):
        """统一解析PoseNet输出（支持字符串/数组格式）"""
        if isinstance(pose_data, str):
            try:
                return np.array(json.loads(pose_data), dtype=np.float32)
            except json.JSONDecodeError:
                print("PoseNet输出JSON解析失败")
                return None
        else:
            return np.array(pose_data, dtype=np.float32)

    def _get_pose_from_frame(self, frame):
        """从视频帧提取姿态数据（含耗时统计+有效关键点计数）"""
        try:
            # 记录姿态提取开始时间
            pose_extract_start = time.time()
            
            # 帧格式转换：cv2默认BGR → PoseNet要求RGB
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 尺寸调整：与PoseNet输入一致（257x257）
            target_h, target_w = 257, 257
            img_resized = cv2.resize(
                img_rgb, 
                (target_w, target_h), 
                interpolation=cv2.INTER_LINEAR
            )
            processed_frame = img_resized.astype(np.uint8)  # 保留预处理后帧用于可视化
            
            # 【关键修改2】调用PoseNet获取3个返回值：姿态数据、是否有姿态、有效关键点数量
            pose_data, has_pose, valid_keypoint_count = get_posenet_output(processed_frame)
            # 处理可能的None值
            valid_keypoint_count = valid_keypoint_count if valid_keypoint_count is not None else 0
            
            # 【关键校验2】有效关键点数量不足，返回无效结果
            if valid_keypoint_count < self.min_valid_keypoints:
                pose_extract_time = time.time() - pose_extract_start
                print(f"帧有效关键点不足（{valid_keypoint_count}/{self.min_valid_keypoints}），无法提取姿态")
                return None, None, pose_extract_time, valid_keypoint_count
            
            # 姿态数据为空的情况
            if pose_data is None or not has_pose:
                pose_extract_time = time.time() - pose_extract_start
                print(f"无法从当前帧中获取姿态数据 | 姿态提取耗时：{pose_extract_time:.4f}s | 有效关键点：{valid_keypoint_count}")
                return None, None, pose_extract_time, valid_keypoint_count
            
            # 统一解析姿态数据
            pose_array = self._parse_pose_data(pose_data)
            # 计算姿态提取耗时
            pose_extract_time = time.time() - pose_extract_start
            print(f"帧姿态提取完成 | 有效关键点：{valid_keypoint_count}/{self.min_valid_keypoints} | 姿态提取耗时：{pose_extract_time:.4f}s")
            return pose_array, processed_frame, pose_extract_time, valid_keypoint_count
        
        except Exception as e:
            pose_extract_time = time.time() - pose_extract_start
            valid_keypoint_count = 0  # 异常时默认关键点数量为0
            print(f"获取帧姿态数据失败：{e} | 姿态提取耗时：{pose_extract_time:.4f}s | 有效关键点：{valid_keypoint_count}")
            return None, None, pose_extract_time, valid_keypoint_count

    # 【新增方法1】绘制关键点不足的红色提示
    def _draw_insufficient_keypoints(self, frame, valid_count):
        """在帧上绘制“有效关键点不足”的红色提示文本"""
        text = f"有效关键点不足：{valid_count}/{self.min_valid_keypoints}"
        cv2.putText(
            img=frame,
            text=text,
            org=(20, 40),  # 与正常结果文本位置一致，覆盖无效信息
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 0, 255),  # 红色警示
            thickness=2,
            lineType=cv2.LINE_AA
        )
        # 可选：绘制FPS（即使关键点不足也显示帧率）
        fps = 1.0 / self.last_infer_time if self.last_infer_time > 1e-6 else 0.0
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(
            img=frame,
            text=fps_text,
            org=(20, 80),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.9,
            color=(255, 0, 0),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        return frame

    def _draw_result_on_frame(self, frame, formatted_result):
        """在cv2帧上绘制推理结果"""
        # 计算实时FPS（基于总耗时）
        fps = 1.0 / self.last_infer_time if self.last_infer_time > 1e-6 else 0.0
        
        # 绘制类别+置信度
        class_text = f"Pose: {formatted_result['class']} ({formatted_result['confidence']:.1f}%)"
        cv2.putText(
            img=frame,
            text=class_text,
            org=(20, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 255, 0),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        # 绘制FPS（基于总耗时）
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(
            img=frame,
            text=fps_text,
            org=(20, 80),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.9,
            color=(255, 0, 0),
            thickness=2,
            lineType=cv2.LINE_AA
        )
        
        return frame

    def inference_frame(self, frame, model_path=None):
        """实时帧推理入口（含完整耗时统计+有效关键点校验）"""
        # 记录总耗时开始时间
        total_start = time.time()
        result_frame = frame.copy()
        self.processed_image = None
        pose_data = None
        valid_keypoint_count = 0  # 初始化有效关键点数量
        pose_extract_time = 0.0

        try:
            # 模型加载检查
            if model_path and (not self.rknn_lite or self.model_path != os.path.abspath(model_path)):
                self.model_path = os.path.abspath(model_path)
                self.load_model()
            if not self.rknn_lite:
                raise RuntimeError("RKNN模型未加载，无法执行推理")

            # 【关键修改3】调用帧姿态提取，接收4个返回值（新增有效关键点数量）
            pose_data, self.processed_image, pose_extract_time, valid_keypoint_count = self._get_pose_from_frame(frame)
            
            # 【关键校验3】有效关键点不足，直接返回无效结果
            if valid_keypoint_count < self.min_valid_keypoints:
                # 生成无效结果格式
                raw_result = np.zeros(len(self.classes)) if self.classes else np.array([])
                formatted_result = {
                    "class": "null",
                    "confidence": 0.0,
                    "probabilities": raw_result.tolist(),
                    "class_id": -1
                }
                # 计算总耗时并更新FPS
                total_time = time.time() - total_start
                self.last_infer_time = total_time
                # 绘制关键点不足提示
                result_frame = self._draw_insufficient_keypoints(result_frame, valid_keypoint_count)
                # 打印日志
                print(f"帧推理终止（有效关键点不足） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：0.0000s | FPS：{1/total_time:.1f}")
                return raw_result, formatted_result, result_frame

            # 姿态数据为空（非关键点不足的其他情况）
            if pose_data is None or self.processed_image is None:
                total_time = time.time() - total_start
                self.last_infer_time = total_time
                print(f"帧推理跳过 | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：0.0000s | FPS：{1/total_time:.1f}")
                return None, None, result_frame

            # 姿态数据预处理
            input_data = self._preprocess(pose_data)
            if input_data is None:
                total_time = time.time() - total_start
                self.last_infer_time = total_time
                print(f"帧推理失败（预处理失败） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：0.0000s | FPS：{1/total_time:.1f}")
                return None, None, result_frame

            # RKNN核心推理（单独统计推理耗时）
            infer_start = time.time()
            outputs = self.rknn_lite.inference(inputs=[input_data])
            rknn_infer_time = time.time() - infer_start  # RKNN推理耗时
            raw_output = outputs[0]
            
            # 结果后处理
            raw_result = raw_output[0].flatten() if raw_output.ndim > 1 else raw_output.flatten()
            formatted_result = self._format_result(raw_result)

            # 帧结果可视化
            result_frame = self._draw_result_on_frame(result_frame, formatted_result)

            # 计算总耗时（从方法开始到推理完成）
            total_time = time.time() - total_start
            self.last_infer_time = total_time  # 更新最后一帧总耗时（用于FPS计算）
            
            # 打印完整耗时信息
            print(f"帧推理完成 | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：{rknn_infer_time:.4f}s | FPS：{1/total_time:.1f} | 结果：{formatted_result['class']}")

            return raw_result, formatted_result, result_frame

        except Exception as e:
            # 异常情况下也统计耗时
            total_time = time.time() - total_start
            rknn_infer_time = 0.0  # 推理未执行，耗时为0
            self.last_infer_time = total_time
            print(f"帧推理失败：{e} | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：{rknn_infer_time:.4f}s | FPS：{1/total_time:.1f}")
            return None, None, result_frame

    def inference(self, data, model_path=None):
        """RKNN推理（含完整耗时统计+有效关键点校验）"""
        # 记录总耗时开始时间
        total_start = time.time()
        self.processed_image = None
        pose_data = None
        raw_result = None
        formatted_result = None
        pose_extract_time = 0.0  # 默认为0（若输入已为姿态数据，无需提取）
        valid_keypoint_count = 0  # 初始化有效关键点数量

        try:
            # 模型加载检查
            if model_path and (not self.rknn_lite or self.model_path != os.path.abspath(model_path)):
                self.model_path = os.path.abspath(model_path)
                self.load_model()
            if not self.rknn_lite:
                raise RuntimeError("RKNN模型未加载，无法执行推理")
            
            # 处理输入数据
            if isinstance(data, str):
                # 【关键修改4】输入为图像路径：接收3个返回值（新增有效关键点数量）
                pose_data, pose_extract_time, valid_keypoint_count = self._get_pose_from_image(data)
                
                # 【关键校验4】有效关键点不足，返回无效结果
                if valid_keypoint_count < self.min_valid_keypoints:
                    raw_result = np.zeros(len(self.classes)) if self.classes else np.array([])
                    formatted_result = {
                        "class": "null",
                        "confidence": 0.0,
                        "probabilities": raw_result.tolist(),
                        "class_id": -1
                    }
                    total_time = time.time() - total_start
                    print(f"推理终止（有效关键点不足） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：0.0000s")
                    return raw_result, formatted_result
                
                # 姿态数据为空（非关键点不足的其他情况）
                if pose_data is None:
                    total_time = time.time() - total_start
                    print(f"推理终止（姿态数据为空） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：0.0000s")
                    return None, None
            else:
                # 输入为已提取的姿态数据，无需提取（默认关键点充足，跳过校验）
                pose_data = data
                valid_keypoint_count = "未知（输入为姿态数据）"
                print(f"输入为姿态数据，跳过图像处理 | 姿态提取耗时：0.0000s | 有效关键点：{valid_keypoint_count}")
            
            # 数据预处理
            input_data = self._preprocess(pose_data)
            if input_data is None:
                total_time = time.time() - total_start
                print(f"推理终止（预处理失败） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | RKNN推理耗时：0.0000s")
                return None, None
            
            # RKNN推理（单独统计推理耗时）
            infer_start = time.time()
            outputs = self.rknn_lite.inference(inputs=[input_data])
            rknn_infer_time = time.time() - infer_start  # RKNN推理耗时
            raw_output = outputs[0]
            
            # 结果后处理
            raw_result = raw_output[0].flatten() if raw_output.ndim > 1 else raw_output.flatten()
            formatted_result = self._format_result(raw_result)
            
            # 结果可视化
            if self.processed_image is not None and formatted_result:
                bgr_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                # 若为关键点不足的无效结果，绘制红色提示；否则绘制正常结果
                if formatted_result["class"] == "null":
                    text = f"有效关键点不足：{valid_keypoint_count}/{self.min_valid_keypoints}"
                    cv2.putText(bgr_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    text = f"{formatted_result['class']} {formatted_result['confidence']:.1f}%"
                    cv2.putText(bgr_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imwrite(self.result_image_path, bgr_image)
                print(f"结果图已保存至：{self.result_image_path} | {text}")
            
            # 计算总耗时并打印完整信息
            total_time = time.time() - total_start
            print(f"推理完成：")
            print(f"- 总耗时：{total_time:.4f}秒")
            print(f"- 姿态提取耗时：{pose_extract_time:.4f}秒")
            print(f"- RKNN推理耗时：{rknn_infer_time:.4f}秒")
            print(f"- 有效关键点：{valid_keypoint_count}/{self.min_valid_keypoints}")
            
            # 将时间信息添加到formatted结果中，以便pose.py获取
            if formatted_result:
                formatted_result['pose_extract_time'] = pose_extract_time
                formatted_result['inference_time'] = rknn_infer_time
                formatted_result['total_time'] = total_time
        
        except Exception as e:
            # 异常情况下也统计耗时
            total_time = time.time() - total_start
            rknn_infer_time = 0.0  # 推理未执行，耗时为0
            print(f"推理失败：{e}")
            print(f"- 总耗时：{total_time:.4f}秒")
            print(f"- 姿态提取耗时：{pose_extract_time:.4f}秒")
            print(f"- RKNN推理耗时：{rknn_infer_time:.4f}秒")
            print(f"- 有效关键点：{valid_keypoint_count}/{self.min_valid_keypoints}")
        
        return raw_result, formatted_result

    def _format_result(self, predictions):
        """结果格式化逻辑"""
        predictions = np.array(predictions, dtype=np.float32)
        class_idx = np.argmax(predictions)
        current_max = predictions[class_idx]
        
        # 生成格式化结果
        confidence = float(predictions[class_idx] * 100)
        return {
            "class": self.classes[class_idx] if 0 <= class_idx < len(self.classes) else f"未知类别_{class_idx}",
            "confidence": confidence,
            "probabilities": predictions.tolist(),
            "class_id": int(class_idx)
        }

    def show_result(self):
        """结果显示逻辑"""
        try:
            result_image = cv2.imread(self.result_image_path)
            if result_image is not None:
                cv2.imshow("Pose RKNN Inference Result", result_image)
                print("按任意键关闭窗口...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                if self.processed_image is None:
                    print("无法显示结果：输入为姿态数据，未生成图像")
                else:
                    print("未找到结果图片，请先执行图像路径输入的推理")
        except Exception as e:
            print(f"显示结果失败：{e}")

    def release(self):
        """释放RKNN资源"""
        if hasattr(self, "rknn_lite") and self.rknn_lite:
            self.rknn_lite.release()
            print("RKNN NPU资源已释放")

    def __del__(self):
        """析构函数自动释放资源"""
        self.release()

    # 便捷接口
    def predict(self, image_path):
        """从图像路径推理（同步接口）"""
        return self.inference(image_path)

    def predict_pose_data(self, pose_data):
        """从已提取的姿态数据推理（同步接口）"""
        return self.inference(pose_data)


# 实时摄像头推理测试
if __name__ == "__main__":
    # 配置参数（替换为你的RKNN模型路径）
    RKNN_MODEL_PATH = "your_pose_model.rknn"
    CAMERA_INDEX = 0  # 0=默认摄像头

    # 初始化姿态推理工作流
    pose_workflow = PoseWorkflow(model_path=RKNN_MODEL_PATH)
    if not pose_workflow.rknn_lite:
        print("RKNN模型初始化失败，无法启动实时推理")
        exit(1)

    # 初始化摄像头
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"无法打开摄像头（索引：{CAMERA_INDEX}）")
        pose_workflow.release()
        exit(1)

    # 设置摄像头分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("实时姿态推理启动成功！")
    print(f"模型路径：{RKNN_MODEL_PATH}")
    print(f"最小有效关键点：{pose_workflow.min_valid_keypoints}个")
    print("按 'q' 键退出实时推理...")

    # 循环读取摄像头帧并推理
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧，退出循环")
            break

        # 执行帧推理（自动打印完整耗时）
        _, _, result_frame = pose_workflow.inference_frame(frame)

        # 显示带标注的帧
        cv2.imshow("RKNN Real-Time Pose Inference", result_frame)

        # 按'q'退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("用户触发退出")
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    pose_workflow.release()
    print("实时推理结束，资源已释放")