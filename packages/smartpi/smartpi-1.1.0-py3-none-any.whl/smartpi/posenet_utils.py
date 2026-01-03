import tensorflow as tf
import cv2
import numpy as np
import os
import sys
from pathlib import Path

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（假设posenet_utils.py位于pose/lib目录下）
project_root = os.path.abspath(os.path.join(script_dir, '..'))

# 全局变量存储模型解释器和相关信息
_interpreter = None
_input_details = None
_output_details = None
# 使用绝对路径定义模型路径
_MODEL_PATH = os.path.join(project_root, 'posemodel', 'posenet.tflite')  # 默认模型路径

# 人体姿态判断参数（可根据需求调整）
POSE_THRESHOLD = 0.3  # 单个关键点分数阈值
REQUIRED_KEYPOINTS = 3  # 判断存在人体所需的有效关键点数量
# 关键人体关节点索引（对应COCO数据集17个关键点）
KEY_KEYPOINTS = [0, 1, 2, 3, 4, 5, 6, 7]  # 头部、颈部、肩膀、肘部等关键节点


def _load_posenet_model(model_path):
    """内部函数：加载Posenet TFLite模型"""
    try:
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        return interpreter, input_details, output_details
    except Exception as e:
        raise FileNotFoundError(f"模型加载失败: {str(e)}")


def _preprocess_image(image_path, input_size=(257, 257)):
    """内部函数：预处理图像，对齐Web端逻辑"""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图像: {image_path}")

    # 转为RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    return _preprocess_common(img_rgb, input_size)


def _preprocess_frame(frame, input_size=(257, 257)):
    """内部函数：预处理视频帧（numpy数组）"""
    # 确保输入是BGR格式（OpenCV默认格式）
    if len(frame.shape) != 3 or frame.shape[2] != 3:
        raise ValueError(f"无效的帧格式，期望3通道BGR图像，实际为{frame.shape}")

    # 转为RGB
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    return _preprocess_common(img_rgb, input_size)


def _preprocess_common(img_rgb, input_size=(257, 257)):
    """通用预处理逻辑，供图像和帧处理共享"""
    # 计算缩放比例
    scale = min(input_size[0]/img_rgb.shape[1], input_size[1]/img_rgb.shape[0])
    scaled_width = int(img_rgb.shape[1] * scale)
    scaled_height = int(img_rgb.shape[0] * scale)

    # 缩放图像（使用线性插值平衡速度和质量）
    img_scaled = cv2.resize(img_rgb, (scaled_width, scaled_height), interpolation=cv2.INTER_LINEAR)

    # 创建257x257画布，居中放置缩放后的图像
    img_padded = np.ones((input_size[1], input_size[0], 3), dtype=np.uint8) * 255
    x_offset = (input_size[0] - scaled_width) // 2
    y_offset = (input_size[1] - scaled_height) // 2
    img_padded[y_offset:y_offset+scaled_height, x_offset:x_offset+scaled_width, :] = img_scaled

    # 归一化
    img_normalized = (img_padded.astype(np.float32) / 127.5) - 1.0

    # 添加批次维度
    return np.expand_dims(img_normalized, axis=0)


def _has_human_pose(heatmap_scores):
    """判断是否存在人体姿态"""
    # heatmap_scores形状为 (height, width, num_keypoints)
    num_keypoints = heatmap_scores.shape[2]

    # 检查关键节点索引是否有效
    valid_keypoints = [k for k in KEY_KEYPOINTS if k < num_keypoints]
    if not valid_keypoints:
        return False, 0

    # 计算每个关键点的最大分数（在整个热图上的最大值）
    keypoint_max_scores = []
    for k in valid_keypoints:
        # 取当前关键点通道的最大分数
        max_score = np.max(heatmap_scores[..., k])
        keypoint_max_scores.append(max_score)

    # 统计超过阈值的关键点数量
    valid_count = sum(1 for score in keypoint_max_scores if score >= POSE_THRESHOLD)

    # 判断是否达到所需数量
    has_pose = valid_count >= REQUIRED_KEYPOINTS
    return has_pose, valid_count


def get_posenet_output(input_data, model_path=None, output_file=None,
                       heatmap_file="heatmap.txt", offsets_file="offsets.txt", precision=6):
    """
    获取输入的posenet输出，支持图像路径或视频帧(numpy数组)

    参数:
        input_data: 图像文件路径(str)或视频帧(numpy.ndarray，BGR格式)
        model_path: 可选，模型文件路径，默认使用 _MODEL_PATH
        output_file: 可选，拼接后的输出txt文件路径，若为None则不保存
        heatmap_file: 可选，heatmap数据保存路径，若为None则不保存
        offsets_file: 可选，offsets数据保存路径，若为None则不保存
        precision: 数据保存精度（小数位数），默认6位

    返回:
        元组 (posenet_output, has_pose, valid_keypoint_count)
            posenet_output: 处理后的一维数组
            has_pose: 是否检测到人体姿态（bool）
            valid_keypoint_count: 有效关键点数量
    """
    global _interpreter, _input_details, _output_details, _MODEL_PATH

    # 如果指定了新的模型路径或模型未加载，则重新加载模型
    if model_path is not None or _interpreter is None:
        model_to_load = model_path if model_path is not None else _MODEL_PATH
        _interpreter, _input_details, _output_details = _load_posenet_model(model_to_load)

    # 根据输入类型选择预处理方式
    if isinstance(input_data, str):
        # 处理图像路径
        input_tensor = _preprocess_image(input_data)
    elif isinstance(input_data, np.ndarray):
        # 处理视频帧（numpy数组）
        input_tensor = _preprocess_frame(input_data)
    else:
        raise TypeError(f"不支持的输入类型: {type(input_data)}，请提供图像路径或numpy数组")

    # 执行推理（复用全局解释器，避免重复初始化）
    _interpreter.set_tensor(_input_details[0]['index'], input_tensor)
    _interpreter.invoke()

    # 按名称匹配输出张量
    output_dict = {}
    for output in _output_details:
        output_name = output['name']
        output_tensor = _interpreter.get_tensor(output['index']).squeeze(axis=0)
        output_dict[output_name] = output_tensor

    # 提取heatmap和offsets，对heatmap应用Sigmoid激活
    heatmap = output_dict['MobilenetV1/heatmap_2/BiasAdd']
    offsets = output_dict['MobilenetV1/offset_2/BiasAdd']

    # 对heatmap应用Sigmoid激活，与TFJS侧的heatmapScores保持一致
    def sigmoid(x):
        x = np.clip(x, -500, 500)  # 限制输入范围，防止exp计算溢出
        return 1 / (1 + np.exp(-x))

    # 生成激活后的heatmap分数（范围[0,1]，与训练数据一致）
    heatmap_scores = sigmoid(heatmap)

    # 判断是否存在人体姿态
    has_pose, valid_count = _has_human_pose(heatmap_scores)

    # 拼接激活后的heatmap和offsets（保持与TFJS侧顺序一致）
    concatenated = np.concatenate([heatmap_scores, offsets], axis=2)
    posenet_output = concatenated.astype(np.float32).flatten()

    # 保存拼接后的输出（仅当指定了路径且输入是图像时）
    if output_file is not None and isinstance(input_data, str):
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            for value in posenet_output:
                f.write(f"{value:.{precision}f}\n")
        print(f"拼接后的posenet输出已保存到: {output_file}")

    return posenet_output, has_pose, valid_count


# 配套加载函数：从按行保存的txt文件加载数据
def load_posenet_output(txt_path):
    """从按行保存的txt文件加载posenet_output"""
    if not Path(txt_path).exists():
        raise FileNotFoundError(f"文件不存在: {txt_path}")

    with open(txt_path, 'r', encoding='utf-8') as f:
        # 读取所有行，跳过空行并转换为float
        data = [float(line.strip()) for line in f if line.strip() and not line.strip().startswith('shape:')]

    return np.array(data, dtype=np.float32)


# 加载heatmap或offsets数据的函数
def load_posenet_component(txt_path):
    """从保存的文件加载heatmap或offsets数据，保留原始形状"""
    if not Path(txt_path).exists():
        raise FileNotFoundError(f"文件不存在: {txt_path}")

    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    # 解析形状信息
    shape_line = next(line for line in lines if line.startswith('shape:'))
    shape_str = shape_line.split('shape: ')[1].strip('()')
    shape = tuple(map(int, shape_str.split(',')))

    # 解析数据
    data_lines = [line for line in lines if not line.startswith('shape:')]
    data = np.array([float(line) for line in data_lines], dtype=np.float32)

    # 重塑为原始形状
    return data.reshape(shape)
