# llm_manager.py
# -*- coding: utf-8 -*-
import openai
import json
import os
import sys
import threading
import time
# 获取当前脚本的绝对路径
# 导入MCP意图识别器
from .mcp_intent_recognizer import MCPIntentRecognizer
current_script_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_script_path)

# 添加SDK绝对路径
sdk_path = os.path.join(current_dir, "tencentcloud-speech-sdk-python")
sys.path.append(sdk_path)




# 全局变量，用于存储初始化后的实例
_conversation_manager = None
_llm_client = None
_intent_recognizer = None
_mcp_intent_recognizer = None

# 全局意图映射配置 - 集中管理所有意图
gLOBAL_INTENTS = {}  # 默认空字典

# 非阻塞响应跟踪变量
_response_lock = threading.Lock()
_response_chunks = []  # 存储回复片段的数组
_full_response = ""  # 完整的回复内容
_response_completed = False  # 回复是否完成的标志
_response_error = None  # 错误信息
_stream_callback = None  # 流式回调函数，用于实时处理回复片段


class ConversationManager:
    """对话历史管理器（原逻辑完整迁移）"""
    def __init__(self, system_prompt=None, max_history_length=10):
        """
        初始化对话历史管理器
        :param system_prompt: 系统提示词 (str, 可选)
        :param max_history_length: 最大对话历史长度 (int, 默认10)
        """
        # 生成包含所有意图信息的系统提示词
        intents_description = self._generate_intents_description()
        
        # 默认系统提示词（可外部自定义）
        default_system_prompt = f"你是一个友好、helpful的智能机器人，可以执行一些简单指令，名字叫小鸣同学。请根据用户的问题和需求提供简洁、有用的回答，保持回答简洁自然，符合口语习惯。\n\n比如你可以：{intents_description}等等,聊天涉及上述动作的时候请简单回答最好做到10字以内的回答，比如用户让你敬个礼，你回答好的，向领导敬礼，回答的时候不要有表情符号、特殊符号以及html和语气词等。"
        
        self.system_prompt = system_prompt or default_system_prompt
        self.history = [{"role": "system", "content": self.system_prompt}]
        self.max_history_length = max_history_length  # 从外部传入最大历史长度
        
    def _generate_intents_description(self):
        """
        生成意图描述文本，用于系统提示词
        :return: 意图描述文本 (str)
        """
        if not gLOBAL_INTENTS:
            return "进行简单对话交流"
            
        descriptions = []
        for intent_code, intent_info in gLOBAL_INTENTS.items():
            intent_name = intent_info["name"]
            keywords = "、".join(intent_info["keywords"])
            descriptions.append(f"{intent_name}（可以用{keywords}等关键词触发）")
        return "、".join(descriptions)

    def add_message(self, role, content):
        """
        添加单条对话记录
        :param role: 角色，如"user"或"assistant" (str)
        :param content: 消息内容 (str)
        """
        self.history.append({"role": role, "content": content})
        self._truncate_history()  # 自动截断超长历史

    def _truncate_history(self):
        """
        截断对话历史（按配置的最大长度保留）
        :return: 无返回值 (None)
        """
        if len(self.history) > self.max_history_length + 1:  # +1 是因为保留system prompt
            self.history = [self.history[0]] + self.history[-(self.max_history_length):]

    def get_messages(self):
        """
        获取当前对话历史（返回副本避免外部修改）
        :return: 对话历史列表 (list[dict])，每个元素包含"role"和"content"字段
        """
        return self.history.copy()

    def clear_history(self):
        """
        清空对话历史（仅保留system prompt）
        :return: 无返回值 (None)
        """
        self.history = [self.history[0]]


class IntentRecognizer:
    """意图识别大模型管理器"""
    def __init__(self, api_key, api_base, model="deepseek-v3", provider="deepseek"):
        """
        初始化意图识别大模型管理器
        :param api_key: API密钥 (str)
        :param api_base: API基础URL (str)
        :param model: 模型名称 (str, 默认"deepseek-v3")
        :param provider: 提供商名称 (str, 默认"deepseek")，可选值："deepseek"或"openai"
        """
        # 统一使用新参数格式
        actual_api_key = api_key
        actual_api_base = api_base
        actual_model = model
        
        # 初始化客户端（支持DeepSeek和OpenAI）
        self.client = openai.OpenAI(
            api_key=actual_api_key,
            base_url=actual_api_base
        )
        self.model = actual_model  # 模型名称
        self.provider = provider.lower()  # 提供商名称（deepseek或openai）
        
        # 生成意图识别系统提示词
        self.intent_system_prompt = self._generate_intent_system_prompt()
        
    def _generate_intent_system_prompt(self):
        """
        根据全局意图映射生成意图识别系统提示词
        :return: 意图识别系统提示词 (str)
        """
        # 构建意图列表字符串
        intent_list = []
        for intent_code, intent_info in gLOBAL_INTENTS.items():
            intent_name = intent_info["name"]
            keywords = intent_info["keywords"]
            
            for keyword in keywords:
                intent_list.append(f"           - {keyword}:{intent_code}")
        
        intent_list_text = "\n".join(intent_list)
        
        # 构建完整的系统提示词
        prompt = f"""你是一个意图识别助手，能够准确识别用户的指令意图。请你根据以下规则处理用户的输入：
        1. 仔细分析用户输入，识别其中包含的所有意图
        2. 每个意图必须对应一个预设的意图代码：
{intent_list_text}
        3. 提取每个意图中的参数，并将其放入arg数组中
        4. 请只返回意图JSON字符串，不要添加任何其他解释性文字
        5. 输出格式必须严格遵循标准JSON：
           - 单个意图：{{"intent":1,"arg":[]}}
           - 多个意图：[{{"intent":1,"arg":[]}},{{"intent":1,"arg":[]}}]
        6. 如果没有识别出任何意图，请返回空数组 []
        
        示例:
        用户输入: 请以50速度前进
        输出: {{"intent":1,"arg":["50"]}}
        
        用户输入: 音量调节到50%
        输出: {{"intent":2,"arg":["50"]}}
        
        用户输入: 请先以50速度前进然后把音量调节到50%
        输出: [{{"intent":1,"arg":["50"]}},{{"intent":2,"arg":["50"]}}]
        """
        
        return prompt
    
    def recognize_intent(self, user_input):
        """
        识别用户输入中的意图
        :param user_input: 用户输入文本 (str)
        :return: 意图识别结果列表 (list[dict])，每个字典包含"intent"和"arg"字段
                - intent: 意图代码 (str)
                - arg: 参数列表 (list[str])
        """
        try:
            # 构建用于意图识别的消息
            messages = [
                {"role": "system", "content": self.intent_system_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # 调用大模型进行意图识别
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.0  # 低温度保证输出稳定性
            )
            
            # 获取大模型回复
            intent_text = response.choices[0].message.content.strip()
            print(f"=====================================意图识别结果：{intent_text}=================================")

            
            # 解析意图JSON
            return self._parse_intent_result(intent_text)
            
        except Exception as e:
            print(f"意图识别失败: {str(e)}")
            return []
    
    def _parse_intent_result(self, intent_text):
        """
        解析意图识别结果
        :param intent_text: 大模型返回的意图文本 (str)
        :return: 解析后的意图识别结果列表 (list[dict])，每个字典包含"intent"和"arg"字段
                - intent: 意图代码 (str)
                - arg: 参数列表 (list[str])
        """
        try:
            # 处理可能的格式问题
            if not intent_text or intent_text == "[]":
                return []
                
            print(f"原始意图文本: {intent_text}")
            
            # 第一步：确保所有双花括号都被替换为单花括号
            # 有时候大模型可能返回 {{intent:"1",arg:[]}} 这种格式
            intent_text = intent_text.replace("{{", "{").replace("}}", "}")
            
            # 第二步：尝试多种解析策略
            # 策略1：尝试作为单个JSON对象解析
            try:
                if intent_text.startswith("{"):
                    intent_data = json.loads(intent_text)
                    print(f"策略1成功，解析到单个意图")
                    return [intent_data]
            except Exception as e1:
                print(f"策略1失败: {str(e1)}")
                
            # 策略2：尝试作为JSON数组解析
            try:
                if not intent_text.startswith("["):
                    formatted_text = "[" + intent_text + "]"
                    intents = json.loads(formatted_text)
                else:
                    intents = json.loads(intent_text)
                
                if isinstance(intents, list):
                    print(f"策略2成功，解析到{len(intents)}个意图")
                    return intents
                elif isinstance(intents, dict):
                    print(f"策略2成功，解析到1个意图")
                    return [intents]
            except Exception as e2:
                print(f"策略2失败: {str(e2)}")
                
            # 策略3：处理可能包含多个意图的情况（以,分隔）
            try:
                # 去除所有空白字符
                clean_text = ''.join(intent_text.split())
                
                if ",{" in clean_text:
                    # 分割多个意图
                    intent_parts = clean_text.split(",")
                    intents = []
                    for i, part in enumerate(intent_parts):
                        try:
                            # 确保每个部分都是有效的JSON对象
                            if not part.startswith("{"):
                                part = "{" + part
                            if not part.endswith("}"):
                                part = part + "}"
                            intent_data = json.loads(part)
                            intents.append(intent_data)
                            print(f"策略3成功，分割并解析到第{i+1}个意图: {intent_data}")
                        except Exception as e_inner:
                            print(f"解析第{i+1}个意图失败: {str(e_inner)}")
                            pass
                    if intents:
                        return intents
            except Exception as e3:
                print(f"策略3失败: {str(e3)}")
                
            # 策略4：尝试修复格式后再解析（更严格的处理）
            try:
                # 去除所有空白字符
                clean_text = ''.join(intent_text.split())
                
                # 确保是对象或数组格式
                if not clean_text.startswith("{") and not clean_text.startswith("["):
                    # 尝试添加对象括号
                    if clean_text.startswith("intent") or ":" in clean_text:
                        clean_text = "{" + clean_text + "}"
                        intent_data = json.loads(clean_text)
                        print(f"策略4成功，修复为对象并解析")
                        return [intent_data]
                else:
                    # 再次尝试解析
                    intent_data = json.loads(clean_text)
                    if isinstance(intent_data, list):
                        print(f"策略4成功，解析到数组")
                        return intent_data
                    else:
                        print(f"策略4成功，解析到对象")
                        return [intent_data]
            except Exception as e4:
                print(f"策略4失败: {str(e4)}")
                
            # 所有策略都失败
            print("所有解析尝试都失败了，返回空列表")
            return []
        except Exception as e:
            print(f"解析意图结果时发生严重错误: {str(e)}")
            return []


class LLMClient:
    """大模型客户端（支持DeepSeek和OpenAI接口）"""
    def __init__(self, api_key=None, api_base=None, 
                 model="deepseek-v3", llm_timeout=10.0,
                 llm_temperature=0.7, llm_max_tokens=200, max_history_length=10,
                 provider="deepseek"):
        """
        初始化大模型客户端
        :param api_key: API密钥 (str, 可选)
        :param api_base: API基础URL (str, 可选)
        :param model: 模型名称 (str, 默认"deepseek-v3")
        :param llm_timeout: 超时时间 (float, 默认10.0秒)
        :param llm_temperature: 温度参数 (float, 默认0.7)
        :param llm_max_tokens: 最大生成 tokens (int, 默认200)
        :param max_history_length: 最大历史长度 (int, 默认10)
        :param provider: 提供商名称 (str, 默认"deepseek")，可选值："deepseek"或"openai"
        """
        # 统一使用新参数格式
        actual_api_key = api_key
        actual_api_base = api_base
        actual_model = model
        
        # 初始化客户端（支持DeepSeek和OpenAI）
        self.client = openai.OpenAI(
            api_key=actual_api_key,
            base_url=actual_api_base,
            timeout=llm_timeout  # 超时时间
        )
        self.model = actual_model  # 模型名称
        self.provider = provider.lower()  # 提供商名称（deepseek或openai）
        self.is_generating = False  # 生成状态标记
        self.current_response = None  # 存储当前响应对象
        self.max_history_length = max_history_length  # 最大历史长度
        
        # 生成参数
        self.generation_params = {
            "temperature": llm_temperature,  # 温度参数
            "max_tokens": llm_max_tokens,  # 最大生成 tokens
            "top_p": 0.9,  # 控制多样性
            "stream": True  # 启用流式输出
        }

    def generate_stream(self, messages, is_running):
        """
        流式调用大模型（优化版：更快的响应速度）
        :param messages: 对话历史 (list[dict])，每个元素包含"role"和"content"字段
        :param is_running: 主程序运行状态 (bool)，用于中断生成
        :return: 流式返回的文本片段 (str)，使用yield逐个返回
        """
        self.is_generating = True
        full_response = ""  # 累计完整响应
        self.current_response = None

        try:
            # 优化对话历史，减少tokens使用
            optimized_messages = self._optimize_messages(messages)
            
            # 流式调用大模型，使用优化参数
            response = self.client.chat.completions.create(
                model=self.model,
                messages=optimized_messages,
                **self.generation_params
            )
            self.current_response = response

            # 流式处理响应（优化版：更快的片段处理）
            for chunk in response:
                # 检查是否需要中断（主程序退出/手动停止）
                if not is_running or not self.is_generating:
                    # 强制关闭响应流
                    if hasattr(response, 'close'):
                        try:
                            response.close()
                        except:
                            pass
                    break

                # 提取当前片段内容
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    # 立即返回，不做额外处理
                    yield content

            return full_response

        except Exception as e:
            # 异常捕获（返回简化错误信息）
            error_msg = f"抱歉，我现在无法回答你的问题。"
            yield error_msg
            return error_msg

        finally:
            # 无论成功/失败，重置生成状态
            self.is_generating = False
            self.current_response = None

    def _optimize_messages(self, messages):
        """
        优化对话历史，减少tokens使用
        :param messages: 原始对话历史 (list[dict])
        :return: 优化后的对话历史 (list[dict])
        """
        # 如果消息数量过多，只保留最近的几条和系统提示
        if len(messages) > self.max_history_length + 1:
            # 保留系统提示
            system_messages = [msg for msg in messages if msg['role'] == 'system']
            # 保留最近的用户和助手消息
            recent_messages = messages[-(self.max_history_length):]
            return system_messages + recent_messages
        return messages
    
    def stop_generation(self):
        """
        手动停止大模型生成（优化版：更快的中断响应）
        :return: 无返回值 (None)
        """
        # 立即设置标志为False
        self.is_generating = False
        
        # 尝试关闭当前响应流（如果存在）
        if self.current_response and hasattr(self.current_response, 'close'):
            try:
                self.current_response.close()
                print("已强制关闭大模型响应流")
            except Exception as e:
                print(f"关闭响应流时出错: {str(e)}")
        
        # 重置当前响应对象
        self.current_response = None


# 全局初始化函数
def init(api_key=None, api_base=None, 
         model="deepseek-v3", llm_timeout=10.0,
         llm_temperature=0.7, llm_max_tokens=200, max_history_length=10,
         system_prompt=None, global_intents=None, provider="openai", isOpenAi=True,
         stream_callback=None):
    """
    初始化大模型相关组件
    :param api_key: API密钥 (str, 可选)
    :param api_base: API基础URL (str, 可选)
    :param model: 大模型名称 (str, 默认"deepseek-v3")
    :param llm_timeout: 大模型请求超时时间 (float, 默认10.0秒)
    :param llm_temperature: 大模型生成温度 (float, 默认0.7)
    :param llm_max_tokens: 大模型最大生成token数 (int, 默认200)
    :param max_history_length: 最大对话历史长度 (int, 默认10)
    :param system_prompt: 系统提示词 (str, 可选)
    :param global_intents: 全局意图映射配置 (dict, 可选)，默认空字典
                          格式: {"intent_code": {"name": "意图名称", "keywords": ["关键词1", "关键词2"]}}
    :param provider: 大模型提供商 (str, 默认"openai")，可选值："deepseek"或"openai"
    :param isOpenAi: 是否使用OpenAI接口模式 (bool, 默认True)
    :param stream_callback: 流式回调函数 (callable, 可选)，用于实时处理回复片段
                          函数签名: callback(chunk: str)
    :return: 无返回值 (None)
    """
    global _stream_callback
    _stream_callback = stream_callback
    # 根据isOpenAi参数自动设置provider
    if isOpenAi:
        provider = "openai"
    
    # 统一使用新参数格式
    final_api_key = api_key
    final_api_base = api_base
    final_model = model or "deepseek-v3"
    
    global _conversation_manager, _llm_client, _intent_recognizer, gLOBAL_INTENTS
    
    # 设置全局意图映射
    if global_intents is not None:
        gLOBAL_INTENTS = global_intents
    
    # 初始化对话管理器
    _conversation_manager = ConversationManager(
        system_prompt=system_prompt,
        max_history_length=max_history_length
    )
    
    # 初始化大模型客户端（支持DeepSeek和OpenAI）
    _llm_client = LLMClient(
        api_key=final_api_key,
        api_base=final_api_base,
        model=final_model,
        llm_timeout=llm_timeout,
        llm_temperature=llm_temperature,
        llm_max_tokens=llm_max_tokens,
        max_history_length=max_history_length,
        provider=provider
    )
    
    # 初始化意图识别器
    _intent_recognizer = IntentRecognizer(
        api_key=final_api_key,
        api_base=final_api_base,
        model=final_model,
        provider=provider
    )
    
    # 初始化MCP意图识别器
    global _mcp_intent_recognizer
    _mcp_intent_recognizer = MCPIntentRecognizer(global_intents=gLOBAL_INTENTS)
    
    print("大模型组件初始化成功")


def send_message(message, is_running=True):
    """
    发送消息给大模型
    :param message: 用户消息文本 (str)
    :param is_running: 运行状态标记 (bool, 默认True)
    :return: 大模型回复的完整内容 (str)
    """
    global _conversation_manager, _llm_client
    
    if not _conversation_manager or not _llm_client:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    # 添加用户消息到对话历史
    _conversation_manager.add_message("user", message)
    
    # 获取完整对话历史
    messages = _conversation_manager.get_messages()
    
    # 调用大模型获取回复
    full_response = ""
    for chunk in _llm_client.generate_stream(messages, is_running):
        if chunk:
            full_response += chunk
    
    # 添加助手回复到对话历史
    _conversation_manager.add_message("assistant", full_response)
    
    return full_response


def get_response_stream(message, is_running=True):
    """
    获取大模型回复的流式结果
    :param message: 用户消息文本 (str)
    :param is_running: 运行状态标记 (bool, 默认True)
    :return: 流式生成的回复片段 (str)，使用yield逐个返回
    """
    global _conversation_manager, _llm_client
    
    if not _conversation_manager or not _llm_client:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    # 添加用户消息到对话历史
    _conversation_manager.add_message("user", message)
    
    # 获取完整对话历史
    messages = _conversation_manager.get_messages()
    
    # 调用大模型获取流式回复
    full_response = ""
    chunks = []
    for chunk in _llm_client.generate_stream(messages, is_running):
        if chunk:
            chunks.append(chunk)
            full_response += chunk
            yield chunk, False
    
    # 处理最后一个回复片段
    if chunks:
        yield chunks[-1], True
    
    # 添加助手回复到对话历史
    _conversation_manager.add_message("assistant", full_response)


def recognize_intent(message):
    """
    识别用户意图
    :param message: 用户消息文本 (str)
    :return: 意图识别结果列表 (list[dict])，每个字典包含"intent"和"arg"字段
            - intent: 意图代码 (str)
            - arg: 参数列表 (list[str])
    """
    global _intent_recognizer
    
    if not _intent_recognizer:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    return _intent_recognizer.recognize_intent(message)


def recognize_intent_mcp(message):
    """
    使用MCP识别用户意图
    :param message: 用户消息文本 (str)
    :return: 意图识别结果列表 (list[dict])，每个字典包含"intent"和"arg"字段
            - intent: 意图代码 (str)
            - arg: 参数列表 (list[str])
    """
    global _mcp_intent_recognizer
    
    if not _mcp_intent_recognizer:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    return _mcp_intent_recognizer.recognize_intent(message)


def clear_history():
    """
    清空对话历史
    :return: 无返回值 (None)
    """
    global _conversation_manager
    
    if not _conversation_manager:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    _conversation_manager.clear_history()


def stop_generation():
    """
    停止大模型生成
    :return: 无返回值 (None)
    """
    global _llm_client
    
    if not _llm_client:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    _llm_client.stop_generation()


def _async_response_handler(message, is_running):
    """
    异步响应处理函数，在后台线程中运行
    :param message: 用户消息文本 (str)
    :param is_running: 运行状态标记 (bool)
    :return: 无返回值 (None)
    """
    global _conversation_manager, _llm_client
    global _response_chunks, _full_response, _response_completed, _response_error
    
    try:
        # 重置响应状态
        with _response_lock:
            _response_chunks = []
            _full_response = ""
            _response_completed = False
            _response_error = None
        
        # 添加用户消息到对话历史
        _conversation_manager.add_message("user", message)
        
        # 获取完整对话历史
        messages = _conversation_manager.get_messages()
        
        # 调用大模型获取流式回复
        full_response = ""
        chunks = []
        for chunk in _llm_client.generate_stream(messages, is_running):
            if chunk:
                chunks.append(chunk)
                full_response += chunk
                # 更新响应片段
                with _response_lock:
                    _response_chunks.append(chunk)
                    _full_response = full_response
                # 调用流式回调函数（如果已设置）
                if _stream_callback and callable(_stream_callback):
                    try:
                        _stream_callback(chunk, is_last=False)
                    except Exception as e:
                        print(f"流式回调函数执行出错: {str(e)}")
        
        # 所有chunk发送完成后，发送一个空字符串并标记is_last=True以结束TTS合成
        # 这样既避免了重复发送最后一个chunk，又能正确结束TTS合成
        if _stream_callback and callable(_stream_callback):
            try:
                _stream_callback("", is_last=True)
            except Exception as e:
                print(f"流式回调函数执行出错: {str(e)}")
        
        # 添加助手回复到对话历史
        _conversation_manager.add_message("assistant", full_response)
        
        # 标记回复完成
        with _response_lock:
            _full_response = full_response
            _response_completed = True
            _response_error = None
            
    except Exception as e:
        # 处理异常
        error_msg = f"抱歉，我现在无法回答你的问题。"
        with _response_lock:
            _response_chunks.append(error_msg)
            _full_response = error_msg
            _response_completed = True
            _response_error = str(e)


def send_message_async(message, is_running=True):
    """
    非阻塞方式发送消息给大模型
    :param message: 用户消息文本 (str)
    :param is_running: 运行状态标记 (bool, 默认True)
    :return: 无返回值 (None)，结果通过get_response_status等函数获取
    """
    global _conversation_manager, _llm_client
    
    if not _conversation_manager or not _llm_client:
        raise Exception("大模型组件尚未初始化，请先调用init函数")
    
    # 创建并启动后台线程
    thread = threading.Thread(target=_async_response_handler, args=(message, is_running))
    thread.daemon = True
    thread.start()


def get_response_status():
    """
    获取当前响应状态
    :return: 包含状态信息的字典 (dict)
            - completed: 回复是否完成 (bool)
            - chunks: 回复片段列表 (list[str])
            - full_response: 完整回复内容 (str)
            - error: 错误信息 (str或None)
    """
    with _response_lock:
        return {
            "completed": _response_completed,
            "chunks": _response_chunks.copy(),
            "full_response": _full_response,
            "error": _response_error
        }


def get_full_response():
    """
    获取完整回复
    :return: 完整回复内容 (str)，如果未完成返回空字符串
    """
    with _response_lock:
        if _response_completed:
            return _full_response
        return ""


def get_realtime_chunks():
    """
    获取当前收集的实时回复数组
    :return: 当前收集的所有回复片段数组 (list[str])
    """
    with _response_lock:
        return _response_chunks.copy()


def clear_response_cache():
    """
    清除回复缓存
    :return: 无返回值 (None)
    """
    with _response_lock:
        global _response_chunks, _full_response, _response_completed, _response_error
        _response_chunks = []
        _full_response = ""
        _response_completed = False
        _response_error = None


def wait_for_response(timeout=None):
    """
    等待响应完成，可设置超时
    :param timeout: 超时时间（秒），None表示无限等待 (float或None)
    :return: 完整回复内容 (str)
    """
    start_time = time.time()
    
    while True:
        with _response_lock:
            if _response_completed:
                return _full_response
        
        # 检查超时
        if timeout is not None and (time.time() - start_time) > timeout:
            raise TimeoutError("等待响应超时")
        
        time.sleep(0.1)  # 短暂休眠，避免CPU占用过高


def get_global_intents():
    """
    获取全局意图映射
    :return: 全局意图映射字典 (dict)，键为意图代码，值为意图信息字典
    """
    global gLOBAL_INTENTS
    return gLOBAL_INTENTS.copy()  # 返回副本避免外部直接修改


def add_custom_intents(intent_code, name="", keywords=None, en_code="en_code"):
    """
    直接向全局意图映射中添加一条自定义意图
    
    Args:
        intent_code: 意图代码，必须唯一且非空
        name (str): 意图名称
        keywords (list, optional): 意图关键词列表
        en_code (str, optional): 英文代码
    
    Returns:
        bool: 添加成功返回True，失败返回False
    """
    global gLOBAL_INTENTS
    
    if not intent_code:
        print("意图代码不能为空")
        return False
    
    if keywords is None:
        keywords = []
    
    # 创建意图配置
    intent_config = {
        "name": name,
        "keywords": keywords,
        "en_code": en_code
    }
    
    # 添加到全局意图映射
    gLOBAL_INTENTS[intent_code] = intent_config
    print(f"已成功添加自定义意图: {intent_code} - {name}")
    
    # 如果意图识别器已经初始化，更新其系统提示词
    if _intent_recognizer:
        _intent_recognizer.intent_system_prompt = _intent_recognizer._generate_intent_system_prompt()
    
    # 如果对话管理器已经初始化，更新其系统提示词
    if _conversation_manager:
        intents_description = _conversation_manager._generate_intents_description()
    
    # 如果MCP意图识别器已初始化，更新其全局意图映射和英文代码映射
    global _mcp_intent_recognizer
    if _mcp_intent_recognizer:
        _mcp_intent_recognizer.global_intents = gLOBAL_INTENTS
        _mcp_intent_recognizer.update_en_code_mapping()
        print(f"MCP意图识别器已更新，添加新意图: {intent_code} - {name}")
        default_system_prompt = f"你是一个友好、helpful的智能机器人，可以执行一些简单指令，名字叫小鸣同学。请根据用户的问题和需求提供简洁、有用的回答，保持回答简洁自然，符合口语习惯。\n\n比如你可以：{intents_description}等等,聊天涉及上述动作的时候请简单回答最好做到10字以内的回答，比如用户让你敬个礼，你回答好的，向领导敬礼，回答的时候不要有表情符号、特殊符号以及html和语气词等。"
        _conversation_manager.system_prompt = default_system_prompt
        _conversation_manager.history[0]["content"] = default_system_prompt
    
    return True

def get_global_intents_count():
    """
    获取当前全局意图映射中的意图数量
    
    Returns:
        int: 意图数量
    """
    return len(gLOBAL_INTENTS)

def clear_global_intents():
    """
    清空全局意图映射
    
    Returns:
        bool: 清空成功返回True
    """
    global gLOBAL_INTENTS
    
    # 清空全局意图映射
    gLOBAL_INTENTS.clear()
    print("已成功清空所有全局意图")
    
    # 如果意图识别器已经初始化，更新其系统提示词
    if _intent_recognizer:
        _intent_recognizer.intent_system_prompt = _intent_recognizer._generate_intent_system_prompt()
    
    # 如果对话管理器已经初始化，更新其系统提示词
    if _conversation_manager:
        intents_description = _conversation_manager._generate_intents_description()
        default_system_prompt = f"你是一个友好、helpful的智能机器人，可以执行一些简单指令，名字叫小鸣同学。请根据用户的问题和需求提供简洁、有用的回答，保持回答简洁自然，符合口语习惯。\n\n比如你可以：{intents_description}等等,聊天涉及上述动作的时候请简单回答最好做到10字以内的回答，比如用户让你敬个礼，你回答好的，向领导敬礼，回答的时候不要有表情符号、特殊符号以及html和语气词等。"
        _conversation_manager.system_prompt = default_system_prompt
        _conversation_manager.history[0]["content"] = default_system_prompt
    
    # 如果MCP意图识别器已初始化，更新其全局意图映射和英文代码映射
    global _mcp_intent_recognizer
    if _mcp_intent_recognizer:
        _mcp_intent_recognizer.global_intents = gLOBAL_INTENTS
        _mcp_intent_recognizer.update_en_code_mapping()
        print("MCP意图识别器已清空所有意图")
    
    return True


def set_global_intents(intents_dict):
    """
    设置全局意图映射
    :param intents_dict: 新的意图映射字典 (dict)，键为意图代码，值为意图信息字典
    :return: 无返回值 (None)
    """
    global gLOBAL_INTENTS, _intent_recognizer, _conversation_manager, _mcp_intent_recognizer
    
    if not isinstance(intents_dict, dict):
        raise ValueError("意图映射必须是字典类型")
    
    gLOBAL_INTENTS = intents_dict
    
    # 如果意图识别器已初始化，更新其系统提示词
    if _intent_recognizer:
        _intent_recognizer.intent_system_prompt = _intent_recognizer._generate_intent_system_prompt()
    
    # 如果对话管理器已初始化，更新其系统提示词
    if _conversation_manager:
        intents_description = _conversation_manager._generate_intents_description()
        default_system_prompt = f"你是一个友好、helpful的智能机器人，可以执行一些简单指令，名字叫小鸣同学。请根据用户的问题和需求提供简洁、有用的回答，保持回答简洁自然，符合口语习惯。\n\n比如你可以：{intents_description}等等,聊天涉及上述动作的时候请简单回答最好做到10字以内的回答，比如用户让你敬个礼，你回答好的，向领导敬礼，回答的时候不要有表情符号、特殊符号以及html和语气词等。"
        _conversation_manager.system_prompt = default_system_prompt
        _conversation_manager.history[0]["content"] = default_system_prompt
    
    # 如果MCP意图识别器已初始化，更新其全局意图映射和英文代码映射
    if _mcp_intent_recognizer:
        _mcp_intent_recognizer.global_intents = gLOBAL_INTENTS
        _mcp_intent_recognizer.update_en_code_mapping()
        print(f"MCP意图识别器全局意图已更新，当前意图数量: {len(_mcp_intent_recognizer.global_intents)}")
    
    print("全局意图映射已更新")
