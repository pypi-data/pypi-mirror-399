import numpy as np          # 用于数值计算和数组操作
from PIL import Image       # 用于图像文件处理
import cv2                  # 用于视频帧处理（OpenCV）
import os                   # 用于文件路径操作
import json                 # 用于解析元数据JSON文件
from rknnlite.api import RKNNLite  # 用于瑞芯微NPU的RKNN模型推理
import time                 # 用于计时，评估推理性能

class ImageWorkflow:
    """
    图像分类工作流类（适配RKNN Lite）：封装了RKNN Lite模型加载、元数据解析、图像/视频帧预处理、
    NPU推理执行和结果格式化的完整流程，专为瑞芯微NPU硬件加速设计，采用全局归一化（与ONNX分类保持一致）
    支持从图像文件或视频帧（numpy数组）进行推理
    """
    def __init__(self, model_path=None):
        """
        初始化RKNN图像推理工作流实例

        参数:
            model_path: RKNN模型文件路径（.rknn格式），可选，可后续通过load_model加载

        属性说明:
            self.rknn_lite: RKNN Lite推理实例，用于与NPU交互执行模型推理
            self.classes: 类别标签列表，如["猫", "狗", "鸟"]，从元数据文件加载
            self.metadata: 模型元数据字典，存储模型描述等信息
            self.input_shape: 模型输入形状，固定为[1, 224, 3, 224]（[batch, height, channels, width]）
        """
        self.rknn_lite = None  # RKNN Lite推理核心实例
        self.classes = []       # 类别标签列表
        self.metadata = {}      # 模型元数据（如作者、版本等）
        # 固定输入形状：[批量大小, 图像高度, 通道数, 图像宽度]，适配多数RKNN图像分类模型
        self.input_shape = [1, 224, 3, 224]

        # 若初始化时提供模型路径，则自动加载模型
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path):
        """
        加载RKNN模型并初始化NPU运行时，同时解析配套的元数据（主要是类别标签）

        参数:
            model_path: RKNN模型文件路径（.rknn格式）

        执行流程:
            1. 初始化RKNN Lite实例
            2. 加载.rknn模型文件，校验模型完整性
            3. 初始化NPU硬件运行时环境
            4. 自动获取并加载配套的元数据文件（仅读取类别标签）
            5. 强制设置输入形状以确保兼容性
        """
        try:
            # 1. 初始化RKNN Lite核心实例
            self.rknn_lite = RKNNLite()

            # 2. 加载RKNN模型文件，返回错误码需校验
            ret = self.rknn_lite.load_rknn(model_path)
            if ret != 0:
                raise RuntimeError(f'加载RKNN模型失败，错误码: {ret}（请检查模型路径和文件完整性）')

            # 3. 初始化NPU运行时环境（需硬件支持 如：灵芯派）
            ret = self.rknn_lite.init_runtime()
            if ret != 0:
                raise RuntimeError(f'初始化NPU运行时失败，错误码: {ret}（请检查硬件驱动和权限）')

            # 4. 自动获取元数据文件路径并加载（仅关注类别标签）
            metadata_path = self._get_metadata_path(model_path)
            self._load_metadata(metadata_path)

            # 5. 解析并固定输入形状（确保模型输入格式统一）
            self._parse_input_shape()

            print(f"模型加载成功: {model_path}")
            print(f"输入形状: {self.input_shape}")
            print(f"类别数量: {len(self.classes)}")

        except Exception as e:
            print(f"模型加载失败: {e}")

    def _get_metadata_path(self, model_path):
        """
        （私有方法，仅内部调用）获取模型配套的元数据文件路径

        路径逻辑:
            1. 优先查找与模型同名的元数据文件（如model.rknn → model_rknn_metadata.json）
            2. 若未找到，查找模型目录下的通用元数据文件（rknn_metadata.json）

        参数:
            model_path: RKNN模型文件路径

        返回:
            元数据文件的完整路径（即使文件不存在，也返回推导路径）
        """
        # 提取模型所在目录和文件名（不含后缀）
        base_dir = os.path.dirname(model_path)
        base_name = os.path.basename(model_path)
        # 构建与模型同名的元数据文件名（如"model.rknn" → "model_rknn_metadata.json"）
        metadata_name = os.path.splitext(base_name)[0] + '_rknn_metadata.json'
        metadata_path = os.path.join(base_dir, metadata_name)

        # 若同名元数据文件不存在，使用通用文件名
        if not os.path.exists(metadata_path):
            metadata_path = os.path.join(base_dir, 'rknn_metadata.json')
            print(f"未找到同名元数据文件，尝试通用路径: {metadata_path}")

        return metadata_path

    def _load_metadata(self, metadata_path):
        """
        （私有方法，仅内部调用）从JSON格式的元数据文件加载类别标签

        加载内容:
            - classes: 类别标签列表（如["cat", "dog"]）

        参数:
            metadata_path: 元数据JSON文件路径

        说明:
            若元数据文件不存在或解析失败，会默认将类别列表设为空，不影响模型基础推理
        """
        try:
            # 读取JSON文件并解析
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            # 仅提取类别标签（无则为空列表）
            self.classes = metadata.get('classes', [])

            print(f"从 {metadata_path} 加载元数据成功")
            print(f"类别标签: {self.classes}")

        except FileNotFoundError:
            print(f"警告: 元数据文件 {metadata_path} 不存在，将使用默认类别索引")
            self.classes = []
        except json.JSONDecodeError:
            print(f"警告: {metadata_path} 不是合法的JSON文件，将使用默认类别索引")
            self.classes = []
        except Exception as e:
            print(f"加载元数据失败: {e}，将使用默认类别索引")
            self.classes = []

    def _parse_input_shape(self):
        """
        （私有方法，仅内部调用）强制设置模型输入形状，确保兼容性

        说明:
            固定输入形状为[1, 224, 3, 224]（[batch, height, channels, width]），
            避免因模型导出时的动态维度（如-1）导致NPU推理异常，适配多数图像分类场景
        """
        self.input_shape = [1, 224, 3, 224]
        print(f"强制使用输入形状: {self.input_shape}（确保NPU推理兼容性）")

    def _preprocess(self, image_path):
        """
        （私有方法，仅内部调用）图像文件预处理：将图像转为RKNN模型要求的输入格式

        预处理流程（与ONNX版本保持一致的全局归一化）:
            1. 读取图像文件并转为RGB格式（去除Alpha通道，避免干扰）
            2. 调整图像尺寸至224×224（匹配输入形状的height和width）
            3. 像素值归一化（0-255 → 0-1）并转为float32类型（全局归一化）
            4. 调整维度顺序（HWC → HCW），匹配输入形状的[height, channels, width]
            5. 添加batch维度，最终形状为[1, 224, 3, 224]

        参数:
            image_path: 图像文件路径（如"test.jpg"、"sample.png"）

        返回:
            预处理后的numpy数组（形状为[self.input_shape]），失败则返回None
        """
        try:
            # 1. 读取图像并转为RGB（PIL默认读取为RGB，部分格式需显式转换）
            img = Image.open(image_path).convert("RGB")

            # 2. 从输入形状提取目标尺寸：height=224，width=224
            target_h, target_w = self.input_shape[1], self.input_shape[3]
            # 双线性插值调整尺寸（平衡速度和画质）
            img = img.resize((target_w, target_h), Image.BILINEAR)

            # 3. 转为numpy数组并全局归一化（像素值从0-255映射到0-1）
            img_array = np.array(img).astype(np.float32) / 255.0  # 形状: [224, 224, 3]（HWC）

            # 4. 调整维度顺序：HWC（高度、宽度、通道）→ HCW（高度、通道、宽度）
            # 匹配RKNN输入形状的[height, channels, width]要求
            img_array = img_array.transpose(0, 2, 1)  # 维度索引0=H,1=W,2=C → 转置后0=H,1=C,2=W

            # 5. 添加batch维度（模型要求输入为[batch, H, C, W]，批量大小=1）
            return np.expand_dims(img_array, axis=0)  # 最终形状: [1, 224, 3, 224]

        except FileNotFoundError:
            print(f"图像预处理失败: 图像文件 {image_path} 不存在")
            return None
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return None

    def inference(self, data, model_path=None):
        """
        从图像文件执行RKNN模型推理（适用于单张图像分类）

        参数:
            data: 图像文件路径（如"test.jpg"）
            model_path: 可选，若未加载模型则从该路径加载

        返回:
            raw: 原始推理结果（numpy数组，形状为[n_classes]，存储每个类别的概率）
            formatted: 格式化结果（字典），包含以下键：
                - 'class': 预测类别名称（或索引）
                - 'confidence': 预测置信度（百分比，0-100）
                - 'probabilities': 所有类别的概率列表

        说明:
            推理过程包含计时功能，可用于评估单张图像的处理速度
        """
        start_time = time.time()  # 记录推理开始时间，用于计算耗时

        # 若未加载模型且提供了路径，则先加载模型
        if model_path and not self.rknn_lite:
            self.load_model(model_path)

        # 预处理图像（转为模型可接受的格式）
        input_data = self._preprocess(data)
        if input_data is None:
            print("推理终止：图像预处理失败")
            return None, None  # 预处理失败则返回空值

        try:
            # 执行RKNN推理：inputs参数为列表（支持多输入模型，此处单输入）
            outputs = self.rknn_lite.inference(inputs=[input_data])
            # 假设模型输出形状为[1, n_classes]，取第一个样本的结果（批量大小=1）
            raw = outputs[0][0]

            # 格式化推理结果（转为人类可读格式）
            formatted = self._format_result(raw)

            # 计算并打印推理总耗时（预处理+推理）
            end_time = time.time()
            print(f"推理耗时: {end_time - start_time:.4f}秒 - 识别结果: {formatted['class']} ({formatted['confidence']}%)")

            return raw, formatted

        except Exception as e:
            print(f"推理失败: {e}")
            return None, None

    def inference_frame(self, frame_data, model_path=None):
        """
        从视频帧数据执行RKNN模型推理（适用于实时视频流处理）

        参数:
            frame_data: 视频帧numpy数组（如OpenCV读取的帧，格式为BGR）
            model_path: 可选，若未加载模型则从该路径加载

        返回:
            raw: 原始推理结果（numpy数组，形状为[n_classes]）
            formatted: 格式化结果（字典），包含以下键：
                - 'class': 预测类别名称（或索引）
                - 'confidence': 预测置信度（百分比）
                - 'probabilities': 所有类别的概率列表
                - 'preprocess_time': 预处理耗时（秒）
                - 'inference_time': 模型推理耗时（秒）

        说明:
            1. 专门适配OpenCV读取的视频帧（默认BGR格式），需转为RGB
            2. 分别测量预处理和推理时间，便于性能分析
        """
        total_start_time = time.time()  # 记录总时间开始

        # 若未加载模型且提供了路径，则先加载模型
        if model_path and not self.rknn_lite:
            self.load_model(model_path)

        # 测量预处理时间
        preprocess_start = time.time()
        # 预处理视频帧（转为模型可接受的格式）
        input_data = self._preprocess_frame(frame_data)
        preprocess_time = time.time() - preprocess_start
        
        if input_data is None:
            print("帧推理终止：帧数据预处理失败")
            return None, None

        try:
            # 测量推理时间
            inference_start = time.time()
            # 执行RKNN推理（NPU硬件加速）
            outputs = self.rknn_lite.inference(inputs=[input_data])
            inference_time = time.time() - inference_start
            
            # 取第一个样本的推理结果（批量大小=1）
            raw = outputs[0][0]

            # 格式化推理结果
            formatted = self._format_result(raw)
            
            # 添加时间信息到返回结果
            formatted['preprocess_time'] = preprocess_time
            formatted['inference_time'] = inference_time

            # 计算总耗时
            total_time = time.time() - total_start_time
            print(f"帧推理耗时: {total_time:.4f}秒 - 识别结果: {formatted['class']} ({formatted['confidence']}%)")

            return raw, formatted

        except Exception as e:
            print(f"帧数据推理失败: {e}")
            return None, None

    def _preprocess_frame(self, frame_data):
        """
        （私有方法，仅内部调用）视频帧数据预处理：适配RKNN模型输入格式

        预处理流程（针对OpenCV帧，与ONNX版本保持一致的全局归一化）:
            1. 校验输入是否为numpy数组（OpenCV帧默认格式）
            2. BGR转RGB（OpenCV默认读取为BGR，模型要求RGB）
            3. 调整尺寸至224×224（线性插值，平衡速度）
            4. 像素值归一化（0-255 → 0-1）并转为float32（全局归一化）
            5. 维度顺序调整（HWC → HCW）
            6. 添加batch维度

        参数:
            frame_data: 视频帧numpy数组（形状通常为[H, W, 3]，BGR格式）

        返回:
            预处理后的numpy数组（形状为[self.input_shape]），失败则返回None
        """
        try:
            # 1. 校验帧数据类型（必须是numpy数组）
            if not isinstance(frame_data, np.ndarray):
                print("错误: 帧数据必须是numpy数组（OpenCV读取的帧格式）")
                return None

            # 2. BGR格式转为RGB格式（模型要求RGB输入）
            img = cv2.cvtColor(frame_data, cv2.COLOR_BGR2RGB)

            # 3. 调整尺寸至目标大小（224×224）
            target_h, target_w = self.input_shape[1], self.input_shape[3]
            # 线性插值（cv2.INTER_LINEAR）：比双线性更快，适合实时场景
            img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LINEAR)

            # 4. 全局归一化并转为float32类型（0-255 → 0-1）
            img_array = img.astype(np.float32) / 255.0  # 形状: [224, 224, 3]（HWC）

            # 5. 调整维度顺序：HWC → HCW（匹配模型输入要求）
            img_array = img_array.transpose(0, 2, 1)  # 0=H,1=W,2=C → 0=H,1=C,2=W

            # 6. 添加batch维度，最终形状: [1, 224, 3, 224]
            return np.expand_dims(img_array, axis=0)

        except Exception as e:
            print(f"帧数据预处理失败: {e}")
            return None

    def _format_result(self, predictions):
        """
        （私有方法，仅内部调用）将原始推理结果格式化为人类可读的字典

        参数:
            predictions: 原始推理结果（numpy数组，形状为[n_classes]，存储每个类别的概率）

        返回:
            格式化结果字典，包含以下键：
                - 'class': 预测类别（若有类别标签则显示名称，否则显示索引）
                - 'confidence': 预测置信度（百分比，四舍五入为整数）
                - 'probabilities': 所有类别的概率列表（保留原始精度）
        """
        # 找到概率最大的类别索引（即预测类别）
        class_idx = np.argmax(predictions)
        # 计算置信度（转为百分比并取整）
        confidence = int(round(predictions[class_idx] * 100))

        # 确定类别名称（若标签列表存在且索引合法，显示名称，否则显示索引）
        if self.classes and 0 <= class_idx < len(self.classes):
            class_name = self.classes[class_idx]
        else:
            class_name = str(class_idx)

        return {
            'class': class_name,
            'confidence': confidence,
            'probabilities': predictions.tolist()  # 转为列表便于后续处理（如JSON序列化）
        }

    def release(self):
        """
        释放RKNN Lite资源和NPU运行时环境

        说明:
            主动调用此方法可避免内存泄漏，尤其在多次创建ImageWorkflow实例时
            析构函数会自动调用此方法，但建议在不需要推理时主动释放
        """
        if hasattr(self, 'rknn_lite') and self.rknn_lite:
            self.rknn_lite.release()
            print("RKNN Lite资源（含NPU运行时）已释放")

    def __del__(self):
        """
        析构函数：对象被销毁时自动释放RKNN资源

        说明:
            确保程序退出或对象回收时，NPU资源被正确释放，避免占用硬件资源
        """
        self.release()


