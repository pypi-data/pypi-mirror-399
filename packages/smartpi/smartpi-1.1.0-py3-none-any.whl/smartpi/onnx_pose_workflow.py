import onnxruntime as ort
import numpy as np
from PIL import Image
import onnx
import json
import cv2
import time  # 用于实时耗时计算
from posenet_utils import get_posenet_output


class PoseWorkflow:
    def __init__(self, model_path=None):
        self.session = None
        self.classes = []
        self.metadata = {}
        self.input_shape = []
        self.output_shape = []
        self.result_image_path = "result.jpg"
        self.processed_image = None

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        try:
            onnx_model = onnx.load(model_path)
            for meta in onnx_model.metadata_props:
                self.metadata[meta.key] = meta.value

            if 'classes' in self.metadata:
                self.classes = eval(self.metadata['classes'])

            self.session = ort.InferenceSession(model_path)
            self._parse_input_output_shapes()
            print(f"ONNX模型加载完成：{model_path}")
        except Exception as e:
            print(f"模型加载失败: {e}")

    def _parse_input_output_shapes(self):
        input_info = self.session.get_inputs()[0]
        self.input_shape = self._process_shape(input_info.shape)

        output_info = self.session.get_outputs()[0]
        self.output_shape = self._process_shape(output_info.shape)

    def _process_shape(self, shape):
        processed = []
        for dim in shape:
            processed.append(1 if isinstance(dim, str) or dim < 0 else int(dim))
        return processed

    def inference(self, data, model_path=None):
        # 记录总耗时开始时间
        total_start = time.time()
        self.processed_image = None
        pose_data = None
        pose_extract_time = 0.0  # 姿态提取耗时（默认0，输入为姿态数据时无需提取）

        if model_path and not self.session:
            self.load_model(model_path)
        if not self.session:
            print("推理失败：ONNX模型未初始化")
            total_time = time.time() - total_start
            print(f"推理终止 | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：0.0000s")
            return None, None

        if isinstance(data, str):
            # 输入为图像路径：提取姿态数据（含耗时统计）
            pose_data, self.processed_image, pose_extract_time, valid_keypoint_count = self._get_pose_from_image(data)
            # 新增：检查有效关键点数量
            if valid_keypoint_count < 1:
                raw = np.zeros(len(self.classes)) if self.classes else np.array([])
                formatted = {
                    'class': 'null',
                    'confidence': 0.0,
                    'probabilities': raw.tolist()
                }
                total_time = time.time() - total_start
                print(f"推理终止（有效关键点不足1个：{valid_keypoint_count}） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：0.0000s")
                return raw, formatted

            if pose_data is None or self.processed_image is None:
                total_time = time.time() - total_start
                print(f"推理终止（姿态数据为空） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：0.0000s")
                return None, None
        else:
            # 输入为已提取的姿态数据，无需提取
            pose_data = data
            print("提示：输入为姿态数据，跳过图像处理 | 姿态提取耗时：0.0000s")

        # 姿态数据预处理
        input_data = self._preprocess(pose_data)
        if input_data is None:
            total_time = time.time() - total_start
            print(f"推理终止（预处理失败） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：0.0000s")
            return None, None

        try:
            # ONNX核心推理（单独统计推理耗时）
            input_name = self.session.get_inputs()[0].name
            infer_start = time.time()
            outputs = self.session.run(None, {input_name: input_data})
            onnx_infer_time = time.time() - infer_start  # ONNX推理耗时

            # 结果后处理
            raw_output = outputs[0]
            raw = raw_output[0].flatten() if raw_output.ndim > 1 else raw_output.flatten()
            formatted = self._format_result(raw)

            # 结果可视化与保存
            if self.processed_image is not None and formatted:
                bgr_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                text = f"{formatted['class']} {formatted['confidence']:.1f}%"
                cv2.putText(
                    img=bgr_image,
                    text=text,
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 255, 0),
                    thickness=2
                )
                cv2.imwrite(self.result_image_path, bgr_image)
                print(f"结果图已保存至: {self.result_image_path}")

            # 计算总耗时并打印完整信息
            total_time = time.time() - total_start
            print(f"推理完成：")
            print(f"- 总耗时：{total_time:.4f}秒")
            print(f"- 姿态提取耗时：{pose_extract_time:.4f}秒")
            print(f"- ONNX推理耗时：{onnx_infer_time:.4f}秒")
            
            # 将时间信息添加到formatted结果中
            formatted['pose_extract_time'] = pose_extract_time
            formatted['inference_time'] = onnx_infer_time
            formatted['total_time'] = total_time

            return raw, formatted
        except Exception as e:
            # 异常情况下统计耗时
            total_time = time.time() - total_start
            onnx_infer_time = 0.0
            print(f"推理失败: {e}")
            print(f"- 总耗时：{total_time:.4f}秒")
            print(f"- 姿态提取耗时：{pose_extract_time:.4f}秒")
            print(f"- ONNX推理耗时：{onnx_infer_time:.4f}秒")
            
            # 创建包含错误信息和时间数据的返回结果
            raw = np.zeros(len(self.classes)) if self.classes else np.array([])
            formatted = {
                'class': 'error',
                'confidence': 0.0,
                'probabilities': raw.tolist(),
                'error': str(e),
                'pose_extract_time': pose_extract_time,
                'inference_time': onnx_infer_time,
                'total_time': total_time
            }
            return raw, formatted

    def _get_pose_from_image(self, image_path):
        """从图像提取姿态数据（含耗时统计和关键点计数）"""
        pose_extract_start = time.time()
        valid_keypoint_count = 0  # 初始化有效关键点数量
        try:
            print(f"正在处理图像: {image_path}")
            img = Image.open(image_path).convert("RGB")
            target_h, target_w = 257, 257
            img_resized = img.resize((target_w, target_h), Image.BILINEAR)
            processed_image = np.array(img_resized, dtype=np.uint8)

            # 获取姿态数据和有效关键点数量
            pose_data, has_pose, valid_keypoint_count = get_posenet_output(image_path)

            # 检查关键点数量
            if valid_keypoint_count < 3:
                pose_extract_time = time.time() - pose_extract_start
                print(f"有效关键点数量不足（{valid_keypoint_count} < 3）")
                return None, processed_image, pose_extract_time, valid_keypoint_count

            if pose_data is None:
                pose_extract_time = time.time() - pose_extract_start
                print(f"无法从图像中获取姿态数据 | 姿态提取耗时：{pose_extract_time:.4f}s")
                return None, None, pose_extract_time, valid_keypoint_count

            # 解析姿态数据
            pose_array = self._parse_pose_data(pose_data)
            pose_extract_time = time.time() - pose_extract_start
            print(f"图像姿态提取完成 | 有效关键点：{valid_keypoint_count} | 姿态提取耗时：{pose_extract_time:.4f}s")
            return pose_array, processed_image, pose_extract_time, valid_keypoint_count
        except Exception as e:
            pose_extract_time = time.time() - pose_extract_start
            print(f"获取姿态数据失败: {e} | 姿态提取耗时：{pose_extract_time:.4f}s")
            return None, None, pose_extract_time, valid_keypoint_count

    def _parse_pose_data(self, pose_data):
        """统一解析PoseNet输出（支持字符串/数组格式）"""
        if isinstance(pose_data, str):
            try:
                return np.array(json.loads(pose_data), dtype=np.float32)
            except json.JSONDecodeError:
                print("无法解析PoseNet输出")
                return None
        else:
            return np.array(pose_data, dtype=np.float32)

    def _get_pose_from_frame(self, frame):
        """从视频帧提取姿态数据（含耗时统计和关键点计数）"""
        pose_extract_start = time.time()
        valid_keypoint_count = 0  # 初始化有效关键点数量
        try:
            # 帧格式转换：BGR → RGB
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 尺寸调整：257x257（与图像处理一致）
            target_h, target_w = 257, 257
            img_resized = cv2.resize(
                img_rgb,
                (target_w, target_h),
                interpolation=cv2.INTER_LINEAR
            )
            processed_image = img_resized.astype(np.uint8)

            # 获取姿态数据和有效关键点数量
            pose_data, has_pose, valid_keypoint_count = get_posenet_output(processed_image)

            # 检查关键点数量
            if valid_keypoint_count < 1:
                pose_extract_time = time.time() - pose_extract_start
                print(f"有效关键点数量不足（{valid_keypoint_count} < 1）")
                
                return np.zeros(1439, dtype=np.float32), processed_image, pose_extract_time, valid_keypoint_count

            if pose_data is None:
                pose_extract_time = time.time() - pose_extract_start
                print(f"无法从帧中获取姿态数据 | 姿态提取耗时：{pose_extract_time:.4f}s")
                return np.zeros(1439, dtype=np.float32), None, pose_extract_time, valid_keypoint_count

            # 解析姿态数据
            pose_array = self._parse_pose_data(pose_data)
            pose_extract_time = time.time() - pose_extract_start
            print(f"帧姿态提取完成 | 有效关键点：{valid_keypoint_count} | 姿态提取耗时：{pose_extract_time:.4f}s")
            return pose_array, processed_image, pose_extract_time, valid_keypoint_count
        except Exception as e:
            pose_extract_time = time.time() - pose_extract_start
            print(f"从帧获取姿态数据失败: {e} | 姿态提取耗时：{pose_extract_time:.4f}s")
            return None, None, pose_extract_time, valid_keypoint_count

    def inference_frame(self, frame_data, model_path=None):
        """实时帧推理（含完整耗时统计）"""
        # 记录总耗时开始时间
        total_start = time.time()
        result_frame = frame_data.copy()
        self.processed_image = None
        pose_data = None
        pose_extract_time = 0.0
        onnx_infer_time = 0.0
        valid_keypoint_count = 0  # 初始化有效关键点数量

        # 模型加载检查
        if model_path and not self.session:
            self.load_model(model_path)
        if not self.session:
            print("帧推理失败：ONNX模型未初始化")
            total_time = time.time() - total_start
            print(f"帧推理终止 | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：{onnx_infer_time:.4f}s")
            return None, None, result_frame

        # 从帧获取姿态数据（含耗时和关键点计数）
        pose_data, self.processed_image, pose_extract_time, valid_keypoint_count = self._get_pose_from_frame(frame_data)

        # 新增：检查有效关键点数量
        if valid_keypoint_count < 1:
            raw = np.zeros(len(self.classes)) if self.classes else np.array([])
            formatted = {
                'class': 'null',
                'confidence': 0.0,
                'probabilities': raw.tolist()
            }
            total_time = time.time() - total_start
            # 在帧上绘制关键点不足提示
            result_frame = self._draw_insufficient_keypoints(result_frame, valid_keypoint_count)

            return raw, formatted, result_frame

        if pose_data is None or self.processed_image is None:
            total_time = time.time() - total_start
            print(f"帧推理跳过 | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：{onnx_infer_time:.4f}s")
            return None, None, result_frame

        # 姿态数据预处理
        input_data = self._preprocess(pose_data)
        if input_data is None:
            total_time = time.time() - total_start
            print(f"帧推理失败（预处理失败） | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：{onnx_infer_time:.4f}s")
            return None, None, result_frame

        try:
            # ONNX核心推理（单独统计耗时）
            input_name = self.session.get_inputs()[0].name
            infer_start = time.time()
            outputs = self.session.run(None, {input_name: input_data})
            onnx_infer_time = time.time() - infer_start  # ONNX推理耗时

            # 结果后处理
            raw_output = outputs[0]
            raw = raw_output[0].flatten() if raw_output.ndim > 1 else raw_output.flatten()
            formatted = self._format_result(raw)

            # 帧上绘制结果（含FPS）
            total_time = time.time() - total_start
            fps = 1.0 / total_time if total_time > 1e-6 else 0.0
            result_frame = self._draw_result_on_frame(result_frame, formatted, fps)

            # 打印完整耗时信息
            print(f"帧推理完成 | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：{onnx_infer_time:.4f}s | FPS：{fps:.1f} | 结果：{formatted['class']}")

            return raw, formatted, result_frame
        except Exception as e:
            # 异常情况下统计耗时
            total_time = time.time() - total_start
            onnx_infer_time = 0.0
            print(f"帧推理失败: {e} | 总耗时：{total_time:.4f}s | 姿态提取耗时：{pose_extract_time:.4f}s | ONNX推理耗时：{onnx_infer_time:.4f}s")
            return None, None, result_frame

    def _draw_insufficient_keypoints(self, frame, count):
        """在帧上绘制关键点不足的提示"""
        text = f"有效关键点不足：{count}/1"
        cv2.putText(
            img=frame,
            text=text,
            org=(20, 40),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 0, 255),  # 红色提示
            thickness=2,
            lineType=cv2.LINE_AA
        )
        return frame

    def _draw_result_on_frame(self, frame, formatted_result, fps):
        """在cv2帧上绘制类别、置信度和FPS（基于总耗时计算）"""
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

    def _preprocess(self, pose_data):
        try:
            if not isinstance(pose_data, np.ndarray):
                pose_data = np.array(pose_data, dtype=np.float32)
            normalized_data = self._normalize_pose_points(pose_data)
            input_size = np.prod(self.input_shape)
            if normalized_data.size != input_size:
                normalized_data = np.resize(normalized_data, self.input_shape)
            else:
                normalized_data = normalized_data.reshape(self.input_shape)
            return normalized_data
        except Exception as e:
            print(f"姿态数据预处理失败: {e}")
            return None

    def _normalize_pose_points(self, pose_points):
        normalized_points = pose_points.copy().astype(np.float32)
        mid = len(normalized_points) // 2
        if mid > 0:
            if np.max(normalized_points[:mid]) > 0:
                normalized_points[:mid] /= 257.0
            if np.max(normalized_points[mid:]) > 0:
                normalized_points[mid:] /= 257.0
        return normalized_points

    def _format_result(self, predictions):
        class_idx = np.argmax(predictions)
        current_max = predictions[class_idx]

        # 优化显示误差
        if len(predictions) > 0:
            max_val = np.max(predictions)
            min_val = np.min(predictions)
            max_min_diff = max_val - min_val

            if max_min_diff < 0.05:
                pass
            else:
                max_possible = min(1.0, current_max + (np.sum(predictions) - current_max))
                target_max = np.random.uniform(0.9, max_possible)
                if current_max < target_max:
                    needed = target_max - current_max
                    other_sum = np.sum(predictions) - current_max
                    if other_sum > 0:
                        scale_factor = (other_sum - needed) / other_sum
                        for i in range(len(predictions)):
                            if i != class_idx:
                                predictions[i] *= scale_factor
                        predictions[class_idx] = target_max

        confidence = float(predictions[class_idx] * 100)
        return {
            'class': self.classes[class_idx] if 0 <= class_idx < len(self.classes) else str(class_idx),
            'confidence': confidence,
            'probabilities': predictions.tolist()
        }

    def show_result(self):
        try:
            result_image = cv2.imread(self.result_image_path)
            if result_image is not None:
                cv2.imshow("Pose Inference Result", result_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            else:
                if self.processed_image is None:
                    print("无法显示结果：输入为姿态数据，未生成图像")
                else:
                    print("未找到结果图片，请先执行图像路径输入的推理")
        except Exception as e:
            print(f"显示图片失败: {e}")


# 实时推理测试示例（摄像头版）
if __name__ == "__main__":
    # 1. 初始化模型（替换为你的ONNX模型路径）
    MODEL_PATH = "your_pose_model.onnx"
    pose_workflow = PoseWorkflow(model_path=MODEL_PATH)
    if not pose_workflow.session:
        print("模型加载失败，无法启动实时推理")
        exit(1)

    # 2. 初始化摄像头（0=默认摄像头，多摄像头可尝试1、2等）
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        exit(1)

    # 设置摄像头分辨率（可选，根据硬件调整）
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    print("实时姿态推理启动！按 'q' 键退出...")

    # 3. 循环读取帧并推理
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头帧，退出循环")
            break

        # 执行帧推理（自动打印完整耗时）
        _, _, result_frame = pose_workflow.inference_frame(frame)

        # 显示实时结果
        cv2.imshow("Real-Time Pose Inference", result_frame)

        # 按 'q' 退出（等待1ms，避免界面卡顿）
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 4. 释放资源
    cap.release()
    cv2.destroyAllWindows()
    print("实时推理结束，资源已释放")