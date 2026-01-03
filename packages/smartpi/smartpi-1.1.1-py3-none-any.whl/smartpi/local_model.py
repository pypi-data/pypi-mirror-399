import os
import sys
import numpy as np

class LocalModel:
    """
    统一管理RKNN和ONNX模型的推理接口
    支持五种分类类型：1-图片、2-手势、3-姿态、4-文字、5-音频
    """
    def __init__(self):
        self.model_type = None  # 模型类型：onnx 或 rknn
        self.classification_type = None  # 分类类型：1-5
        self.workflow = None  # 实际使用的工作流实例
        self.last_result = None  # 缓存的推理结果
        
    def init_model(self, model_path, classification_type):
        """
        初始化模型
        
        :param model_path: 模型文件路径 (str 类型，支持 .onnx 或 .rknn 格式)
        :param classification_type: 分类类型 (int 类型，1-5)
                                   1: 图片, 2: 手势, 3: 姿态, 4: 文字, 5: 音频
        :return: 是否初始化成功 (bool 类型，True 表示成功，False 表示失败)
        """
        try:
            # 验证分类类型
            if classification_type < 1 or classification_type > 5:
                raise ValueError("分类类型必须是1-5之间的整数")
            
            self.classification_type = classification_type
            
            # 根据文件扩展名判断模型类型
            ext = os.path.splitext(model_path)[1].lower()
            if ext == '.onnx':
                self.model_type = 'onnx'
            elif ext == '.rknn':
                self.model_type = 'rknn'
            else:
                raise ValueError("只支持.onnx和.rknn格式的模型文件")
            
            # 根据模型类型和分类类型加载对应的工作流
            self._load_workflow(model_path)
            
            return True
        except Exception as e:
            print(f"模型初始化失败: {e}")
            return False
    
    def _load_workflow(self, model_path):
        """
        根据模型类型和分类类型加载对应的工作流
        """
        module_name = None
        class_name = None
        
        # 根据分类类型和模型类型确定要加载的模块
        if self.classification_type == 1:  # 图片
            module_name = f"{self.model_type}_image_workflow"
            class_name = "ImageWorkflow"
        elif self.classification_type == 2:  # 手势
            module_name = f"{self.model_type}_hand_workflow"
            class_name = "GestureWorkflow"
        elif self.classification_type == 3:  # 姿态
            module_name = f"{self.model_type}_pose_workflow"
            class_name = "PoseWorkflow"
        elif self.classification_type == 4:  # 文字
            module_name = f"{self.model_type}_text_workflow"
            class_name = "TextClassificationWorkflow"
        elif self.classification_type == 5:  # 音频
            module_name = f"{self.model_type}_voice_workflow"
            class_name = "Workflow"
        
        # 动态导入模块
        try:
            # 确保能找到smartpi模块
            if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
                sys.path.append(os.path.abspath(os.path.dirname(__file__)))
            
            # 修复logging模块处理字符串级别的问题
            import logging
            
            # 保存原始的_checkLevel函数
            original_check_level = logging._checkLevel
            
            # 重写_checkLevel函数，使其能处理字符串级别
            def patched_check_level(level):
                if isinstance(level, str):
                    # 将字符串级别转换为对应的常量
                    level = level.upper()
                    if hasattr(logging, level):
                        return getattr(logging, level)
                # 如果是数字或未知字符串，使用原始函数处理
                return original_check_level(level)
            
            # 应用补丁
            logging._checkLevel = patched_check_level
            
            # 确保所有标准日志级别都可用
            for level_name, level_value in [
                ('DEBUG', 10),
                ('INFO', 20),
                ('WARNING', 30),
                ('ERROR', 40),
                ('CRITICAL', 50)
            ]:
                if not hasattr(logging, level_name):
                    logging.addLevelName(level_value, level_name)
                    setattr(logging, level_name, level_value)
            
            # 保存原始的logging配置
            original_logging_level = logging.getLogger().level
            original_logging_handlers = logging.getLogger().handlers.copy()
            
            module = __import__(module_name, fromlist=[class_name])
            workflow_class = getattr(module, class_name)
            
            # 重置日志配置到原始状态
            logging.getLogger().setLevel(original_logging_level)
            logging.getLogger().handlers = original_logging_handlers
            
            # 恢复原始的_checkLevel函数
            logging._checkLevel = original_check_level
            
            # 初始化工作流（文字分类需要特殊处理）
            if self.classification_type == 4:  # 文字分类
                # 文字分类模型需要两个模型文件：特征提取模型和分类模型
                # 这里假设分类模型路径中包含"class"，特征模型在同一目录下
                if "class" in model_path.lower():
                    # 构建特征提取模型路径
                    feature_model_path = model_path.replace("class", "feature")
                    if not os.path.exists(feature_model_path):
                        # 如果找不到带feature的模型，尝试使用默认路径
                        from onnx_text_workflow import default_feature_model, default_tokenizer_path
                        feature_model_path = default_feature_model
                        tokenizer_path = default_tokenizer_path
                    else:
                        tokenizer_path = None
                    
                    self.workflow = workflow_class(model_path, feature_model_path, tokenizer_path)
                else:
                    # 如果没有指定分类模型，使用默认初始化
                    self.workflow = workflow_class(model_path)
            else:
                # 其他类型直接初始化
                self.workflow = workflow_class(model_path)
                
            print(f"成功加载{self.model_type} {self._get_classification_name()}工作流")
            
        except Exception as e:
            print(f"加载工作流失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def predict(self, data):
        """
        执行推理
        
        :param data: 输入数据，根据分类类型不同而不同
                    图片/手势/姿态: 图片路径 (str 类型) 或帧数据 (numpy.ndarray 类型)
                    文字: 文本字符串 (str 类型) 或文本列表 (list[str] 类型)
                    音频: 音频文件路径 (str 类型) 或音频数据 (numpy.ndarray 类型)
        :return: 推理结果，具体类型取决于工作流类型
                可能是 dict、tuple、list 或其他类型，失败时返回 None
        """
        if not self.workflow:
            raise RuntimeError("模型尚未初始化，请先调用init_model")
        
        try:
            result = None
            
            # 根据分类类型选择合适的推理方法
            if self.classification_type in [1, 2, 3]:  # 图片/手势/姿态
                if isinstance(data, str) and os.path.isfile(data):
                    # 输入是文件路径
                    if hasattr(self.workflow, 'inference'):
                        result = self.workflow.inference(data)
                    elif hasattr(self.workflow, 'predict'):
                        result = self.workflow.predict(data)
                    else:
                        raise RuntimeError(f"当前工作流不支持文件路径输入的推理")
                else:
                    # 输入是帧数据
                    if hasattr(self.workflow, 'inference_frame'):
                        result = self.workflow.inference_frame(data)
                    else:
                        raise RuntimeError(f"当前工作流不支持帧数据输入的推理")
            
            elif self.classification_type == 4:  # 文字
                if hasattr(self.workflow, 'predict'):
                    result = self.workflow.predict(data)
                elif hasattr(self.workflow, 'inference'):
                    result = self.workflow.inference(data)
                else:
                    raise RuntimeError(f"当前工作流不支持文字推理")
            
            elif self.classification_type == 5:  # 音频
                if isinstance(data, str) and os.path.isfile(data):
                    # 输入是文件路径
                    if hasattr(self.workflow, 'inference'):
                        result = self.workflow.inference(data)
                    else:
                        raise RuntimeError(f"当前工作流不支持文件路径输入的音频推理")
                else:
                    # 输入是音频数据（ndarray）
                    if hasattr(self.workflow, 'process_audio_segment'):
                        # 完全参考test_voice.py的实现
                        
                        # 调用process_audio_segment处理音频数据，与test_voice.py保持一致
                        block_results, final_result = self.workflow.process_audio_segment(data)
                        
                        # 优先使用final_result（与test_voice.py保持一致）
                        if final_result is not None:
                            result = final_result
                        elif block_results and len(block_results) > 0:
                            # 如果没有最终结果但有块结果，使用第一个块的结果
                            result = block_results[0]['result']
                        else:
                            # 没有任何结果
                            result = None
                    else:
                        raise RuntimeError(f"当前工作流不支持音频数据输入的推理")
            
            # 缓存结果
            self.last_result = result
            
            return result
            
        except Exception as e:
            print(f"推理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict_frame(self, frame):
        """
        实时帧推理（专门用于图片、手势、姿态分类）
        
        :param frame: 图像帧数据 (numpy.ndarray 类型)
        :return: 推理结果，具体类型取决于工作流类型
                可能是 dict、tuple、list 或其他类型，失败时返回 None
        """
        if not self.workflow:
            raise RuntimeError("模型尚未初始化，请先调用init_model")
        
        if self.classification_type not in [1, 2, 3]:
            raise ValueError("predict_frame只支持图片、手势和姿态分类模型")
        
        try:
            if hasattr(self.workflow, 'inference_frame'):
                result = self.workflow.inference_frame(frame)
                self.last_result = result
                return result
            elif hasattr(self.workflow, 'predict_frame'):
                result = self.workflow.predict_frame(frame)
                self.last_result = result
                return result
            else:
                raise RuntimeError(f"当前工作流不支持帧推理")
                
        except Exception as e:
            print(f"帧推理失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_model_result(self, case=1):
        """
        获取推理结果
        
        :param case: 结果类型 (int 类型，默认值为 1)
                    1: 分类结果
                    2: 分类结果的置信度
        :return: 对应的结果，具体类型取决于推理结果的格式
                case=1 时，通常返回 str 或 int 类型
                case=2 时，通常返回 float 类型
                无结果时返回 None
        """
        if not self.last_result:
            return None
        
        # 根据不同的工作流结果格式进行处理
        try:
            # 处理字典类型的结果（音频分类结果通常是这种格式，与test_voice.py保持一致）
            if isinstance(self.last_result, dict):
                if case == 1:
                    return self.last_result.get('class', None)
                elif case == 2:
                    return self.last_result.get('confidence', None)
            
            # 处理元组类型的结果
            elif isinstance(self.last_result, tuple):
                raw_result, formatted_result = self.last_result
                
                if case == 1:  # 分类结果
                    if isinstance(formatted_result, dict):
                        return formatted_result.get('class', None)
                    elif isinstance(formatted_result, list):
                        return formatted_result[0].get('class', None) if formatted_result else None
                    else:
                        return formatted_result
                
                elif case == 2:  # 置信度
                    if isinstance(formatted_result, dict):
                        return formatted_result.get('confidence', None)
                    elif isinstance(formatted_result, list):
                        return formatted_result[0].get('confidence', None) if formatted_result else None
                    elif isinstance(raw_result, list):
                        return max(raw_result[0]) if raw_result else None
                    elif isinstance(raw_result, dict):
                        return max(raw_result.values())
                    else:
                        return raw_result
            
            # 处理列表类型的结果
            elif isinstance(self.last_result, list):
                if case == 1:
                    return self.last_result[0] if self.last_result else None
                elif case == 2:
                    return max(self.last_result) if self.last_result else None
            
            # 默认返回原始结果
            return self.last_result
            
        except Exception as e:
            print(f"获取结果失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def clear_result(self):
        """
        清除结果缓存并释放工作流资源
        
        :return: 无返回值 (None 类型)
        """
        self.last_result = None
        
        # 释放旧的工作流资源
        if self.workflow:
            try:
                if hasattr(self.workflow, 'release'):
                    self.workflow.release()
                self.workflow = None
            except Exception as e:
                print(f"释放工作流资源失败: {e}")
    
    def _get_classification_name(self):
        """
        获取分类类型的名称
        """
        names = {
            1: "图片",
            2: "手势",
            3: "姿态",
            4: "文字",
            5: "音频"
        }
        return names.get(self.classification_type, "未知")

# 全局实例
_local_model_instance = None

def init_model(model_path, classification_type):
    """
    全局初始化模型函数
    
    :param model_path: 模型文件路径 (str 类型，支持 .onnx 或 .rknn 格式)
    :param classification_type: 分类类型 (int 类型，1-5)
                               1: 图片, 2: 手势, 3: 姿态, 4: 文字, 5: 音频
    :return: 是否初始化成功 (bool 类型，True 表示成功，False 表示失败)
    """
    global _local_model_instance
    if not _local_model_instance:
        _local_model_instance = LocalModel()
    return _local_model_instance.init_model(model_path, classification_type)

def predict(data):
    """
    全局推理函数
    
    :param data: 输入数据，根据分类类型不同而不同
                图片/手势/姿态: 图片路径 (str 类型) 或帧数据 (numpy.ndarray 类型)
                文字: 文本字符串 (str 类型) 或文本列表 (list[str] 类型)
                音频: 音频文件路径 (str 类型) 或音频数据 (numpy.ndarray 类型)
    :return: 推理结果，具体类型取决于工作流类型
            可能是 dict、tuple、list 或其他类型，失败时返回 None
    """
    global _local_model_instance
    if not _local_model_instance:
        raise RuntimeError("模型尚未初始化，请先调用init_model")
    return _local_model_instance.predict(data)

def predict_frame(frame):
    """
    全局帧推理函数（专门用于图片、手势、姿态分类）
    
    :param frame: 图像帧数据 (numpy.ndarray 类型)
    :return: 推理结果，具体类型取决于工作流类型
            可能是 dict、tuple、list 或其他类型，失败时返回 None
    """
    global _local_model_instance
    if not _local_model_instance:
        raise RuntimeError("模型尚未初始化，请先调用init_model")
    return _local_model_instance.predict_frame(frame)

def get_model_result(case=1):
    """
    全局获取结果函数
    
    :param case: 结果类型 (int 类型，默认值为 1)
                1: 分类结果
                2: 分类结果的置信度
    :return: 对应的结果，具体类型取决于推理结果的格式
            case=1 时，通常返回 str 或 int 类型
            case=2 时，通常返回 float 类型
            无结果时返回 None
    """
    global _local_model_instance
    if not _local_model_instance:
        raise RuntimeError("模型尚未初始化，请先调用init_model")
    return _local_model_instance.get_model_result(case)

def clear_result():
    """
    全局清除结果函数，用于清除结果缓存并释放工作流资源
    
    :return: 无返回值 (None 类型)
    """
    global _local_model_instance
    if _local_model_instance:
        _local_model_instance.clear_result()