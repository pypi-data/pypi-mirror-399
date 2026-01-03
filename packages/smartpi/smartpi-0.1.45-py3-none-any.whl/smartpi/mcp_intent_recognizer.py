# -*- coding: utf-8 -*-
"""使用MCP优化的意图识别器"""
import asyncio
import json
import re
from typing import List, Dict, Any
from .mcp_client import MCPClient
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPIntentRecognizer:
    """基于MCP的意图识别器"""
    
    def __init__(self, global_intents=None):
        self.mcp_client = None
        self.is_connected = False
        self.server_url = "http://127.0.0.1:8000/mcp"
        self.intent_tool_name = "recognize_intent"
        self.initialize_task = None
        # 初始化标志，避免重复初始化
        self._initializing = False
        # 存储全局意图映射
        self.global_intents = global_intents if global_intents is not None else {}
        
        # 构建英文代码到数字代码的映射
        self.en_code_to_intent_code = {}
        for intent_code, intent_info in self.global_intents.items():
            if "en_code" in intent_info:
                en_code = intent_info["en_code"]
                # 支持单个英文代码或英文代码列表
                if isinstance(en_code, list):
                    for code in en_code:
                        self.en_code_to_intent_code[code.lower()] = intent_code
                else:
                    self.en_code_to_intent_code[en_code.lower()] = intent_code
        
        logger.info(f"MCPIntentRecognizer初始化，全局意图数量: {len(self.global_intents)}, 英文代码映射数量: {len(self.en_code_to_intent_code)}")
    
    def _get_intent_code_from_en_code(self, en_code):
        """
        将英文意图代码转换为数字代码
        
        Args:
            en_code: 英文意图代码
            
        Returns:
            int: 对应的数字代码，如果未找到则返回None
        """
        if not en_code or not isinstance(en_code, str):
            return None
        
        # 转换为小写后查找
        return self.en_code_to_intent_code.get(en_code.lower())
    
    def update_en_code_mapping(self):
        """
        更新英文代码到数字代码的映射
        当全局意图被更新时，需要调用此方法来更新映射
        """
        # 清空旧的映射
        self.en_code_to_intent_code.clear()
        
        # 重新构建映射
        for intent_code, intent_info in self.global_intents.items():
            if "en_code" in intent_info:
                en_code = intent_info["en_code"]
                # 支持单个英文代码或英文代码列表
                if isinstance(en_code, list):
                    for code in en_code:
                        self.en_code_to_intent_code[code.lower()] = intent_code
                else:
                    self.en_code_to_intent_code[en_code.lower()] = intent_code
        
        logger.info(f"英文代码映射已更新，当前映射数量: {len(self.en_code_to_intent_code)}")
    
    async def initialize(self):
        """初始化MCP客户端并连接到服务器"""
        # 避免重复初始化
        if self.is_connected or self._initializing:
            return self.is_connected
        
        self._initializing = True
        
        try:
            self.mcp_client = MCPClient()
            result = await self.mcp_client.connect(self.server_url)
            if result:
                logger.info("成功连接到MCP服务器")
                self.is_connected = True
                return True
            else:
                logger.warning("连接MCP服务器未成功返回")
                self.is_connected = False
                return False
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {str(e)}")
            self.is_connected = False
            return False
        finally:
            self._initializing = False
    
    async def recognize_intent_async(self, user_input: str) -> List[Dict[str, Any]]:
        """异步识别用户输入中的意图"""
        # 确保已连接
        if not self.is_connected:
            await self.initialize()
            if not self.is_connected:
                logger.error("无法连接到MCP服务器")
                return []
        
        try:
            # 构建工具调用请求
            tool_call = {
                "id": "1",
                "type": "function",
                "function": {
                    "name": self.intent_tool_name,
                    "arguments": json.dumps({"user_input": user_input})
                }
            }
            
            # 调用MCP工具
            results = await self.mcp_client.call_tool([tool_call])
            
            # 解析结果
            if results:
                # 遍历所有结果，找到tool类型的响应
                for tool_result in results:
                    if tool_result.get("role") == "tool":
                        intent_result = tool_result.get("content", "[]")
                        logger.info(f"从MCP接收到的意图结果: {intent_result}")
                        parsed_result = self._parse_intent_result(intent_result)
                        
                        # 增强带参数意图识别，无论MCP是否返回结果，都尝试提取参数
                        enhanced_result = []
                        
                        # 1. 如果MCP返回了意图，为每个意图添加参数和名称
                        if parsed_result:
                            for intent_data in parsed_result:
                                # 如果没有参数，尝试提取，但仅对需要参数的意图进行提取
                                if 'arg' not in intent_data or not intent_data['arg']:
                                    intent_code = intent_data['intent']
                                    # 只有特定的意图类型才需要参数（如音量调节、速度调节等）
                                    # 根据意图配置判断是否需要参数，或者直接检查意图代码
                                    # 这里我们假设只有部分意图需要参数，大部分不需要
                                    # 音量调节(2)、速度调节(7)等需要参数的意图列表
                                    parameter_intents = ['2', '7']  # 可以根据实际情况扩展
                                    if intent_code in parameter_intents:
                                        intent_data['arg'] = self._extract_parameters(user_input, intent_code)
                                    else:
                                        # 不需要参数的意图，保持空列表
                                        intent_data['arg'] = []
                                
                                enhanced_result.append(intent_data)
                        else:
                            # 2. 如果MCP没有返回意图，尝试直接从文本中识别音量调节等常见意图
                            enhanced_result = self._direct_extract_intents(user_input)
                        
                        logger.info(f"增强后的意图识别结果: {enhanced_result}")
                        return enhanced_result
        except Exception as e:
            logger.error(f"通过MCP识别意图失败: {str(e)}")
        
        # 如果发生异常，尝试直接从文本中识别意图
        return self._direct_extract_intents(user_input)
    
    def _extract_parameters(self, text, intent):
        """从文本中提取参数"""
        text_lower = text.lower()
        
        # 尝试提取数字参数，支持百分比形式
        numbers = re.findall(r'\d+(?:\.\d+)?', text_lower)
        if numbers:
            return [numbers[0]]  # 返回第一个匹配的数字
        
        return []
    
    def _direct_extract_intents(self, user_input):
        """直接从文本中提取常见意图，特别是带参数的意图"""
        text_lower = user_input.lower()
        result = []
        
        
        
        # 直接使用从ai_llm.py传入的全局意图配置，实现集中管理
        for intent_code, intent_info in self.global_intents.items():
            # 检查意图是否已被识别（避免重复）
            intent_already_identified = any(item["intent"] == intent_code for item in result)
            if intent_already_identified:
                continue
                
            # 检查关键词
            for keyword in intent_info["keywords"]:
                if keyword in text_lower:
                    # 提取参数
                    args = self._extract_parameters(text_lower, intent_code)
                    result.append({
                        "intent": intent_code,
                        "arg": args
                    })
                    break
        
        return result
    
    def recognize_intent(self, user_input: str) -> List[Dict[str, Any]]:
        """同步识别用户输入中的意图（供非异步代码调用）- 仅使用MCP，不包含回退机制"""
        try:
            # 增强日志记录
            logger.info(f"开始意图识别: {user_input}")
            
            # 如果事件循环已存在，使用现有的
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except (RuntimeError, AssertionError):
                # 创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # 尝试通过MCP识别
            result = loop.run_until_complete(self.recognize_intent_async(user_input))
            logger.info(f"意图识别完成，结果: {result}")
            return result
        except Exception as e:
            logger.error(f"同步调用MCP意图识别失败: {str(e)}")
            return []
    

    
    def _parse_intent_result(self, intent_text: str) -> List[Dict[str, Any]]:
        """解析意图识别结果，与FastIntentRecognizer保持一致"""
        try:
            # 处理可能的格式问题
            if not intent_text or intent_text.strip() == "[]":
                return []
                
            # 第一步：确保所有双花括号都被替换为单花括号
            intent_text = intent_text.replace("{{", "{").replace("}}", "}")
            
            # 第二步：尝试多种解析策略
            # 策略1：尝试作为单个JSON对象解析
            try:
                if intent_text.strip().startswith("{"):
                    intent_data = json.loads(intent_text)
                    # 确保返回的格式与FastIntentRecognizer一致
                    if "intent" in intent_data:
                        return [intent_data]
                    # 如果字段名为intent_code，则转换为intent
                    elif "intent_code" in intent_data:
                        converted = {"intent": intent_data["intent_code"]}
                        if "arg" in intent_data:
                            converted["arg"] = intent_data["arg"]
                        return [converted]
            except Exception as e1:
                logger.warning(f"策略1解析失败: {str(e1)}")
                
            # 策略2：尝试作为JSON数组解析
            try:
                if not intent_text.strip().startswith("["):
                    formatted_text = "[" + intent_text + "]"
                    intents = json.loads(formatted_text)
                else:
                    intents = json.loads(intent_text)
                
                # 确保返回的格式与FastIntentRecognizer一致
                if isinstance(intents, list):
                    result = []
                    for intent in intents:
                        if isinstance(intent, dict):
                            if "intent" in intent:
                                result.append(intent)
                            elif "intent_code" in intent:
                                converted = {"intent": intent["intent_code"]}
                                if "arg" in intent:
                                    converted["arg"] = intent["arg"]
                                result.append(converted)
                    return result if result else intents
                elif isinstance(intents, dict):
                    if "intent" in intents:
                        return [intents]
                    elif "intent_code" in intents:
                        converted = {"intent": intents["intent_code"]}
                        if "arg" in intents:
                            converted["arg"] = intents["arg"]
                        return [converted]
                    return [intents]
            except Exception as e2:
                logger.warning(f"策略2解析失败: {str(e2)}")
                
            # 策略3：处理可能包含多个意图的情况
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
                            # 转换格式
                            if "intent" in intent_data:
                                intents.append(intent_data)
                            elif "intent_code" in intent_data:
                                converted = {"intent": intent_data["intent_code"]}
                                if "arg" in intent_data:
                                    converted["arg"] = intent_data["arg"]
                                intents.append(converted)
                        except Exception as e_inner:
                            logger.warning(f"解析第{i+1}个意图失败: {str(e_inner)}")
                            pass
                    if intents:
                        return intents
            except Exception as e3:
                logger.warning(f"策略3解析失败: {str(e3)}")
                
            # 策略4：尝试修复格式后再解析
            try:
                # 去除所有空白字符
                clean_text = ''.join(intent_text.split())
                
                # 确保是对象或数组格式
                if not clean_text.startswith("{") and not clean_text.startswith("["):
                    # 尝试添加对象括号
                    if clean_text.startswith("intent") or ":" in clean_text:
                        clean_text = "{" + clean_text + "}"
                        intent_data = json.loads(clean_text)
                        # 转换格式
                        if "intent" in intent_data:
                            return [intent_data]
                        elif "intent_code" in intent_data:
                            intent_code_value = intent_data["intent_code"]
                            if isinstance(intent_code_value, str) and intent_code_value.isalpha():
                                numeric_code = self._get_intent_code_from_en_code(intent_code_value)
                                if numeric_code:
                                    intent_code_value = numeric_code
                            converted = {"intent": intent_code_value}
                            if "arg" in intent_data:
                                converted["arg"] = intent_data["arg"]
                            return [converted]
                else:
                    # 再次尝试解析
                    intent_data = json.loads(clean_text)
                    if isinstance(intent_data, list):
                        # 检查列表中的每个意图
                        for item in intent_data:
                            if isinstance(item, dict) and "intent" in item:
                                intent_value = item["intent"]
                                if isinstance(intent_value, str) and intent_value.isalpha():
                                    numeric_code = self._get_intent_code_from_en_code(intent_value)
                                    if numeric_code:
                                        item["intent"] = numeric_code
                        return intent_data
                    else:
                        if isinstance(intent_data, dict) and "intent" in intent_data:
                            # 检查intent是否为英文代码，如果是则转换为数字代码
                            intent_value = intent_data["intent"]
                            if isinstance(intent_value, str) and intent_value.isalpha():
                                numeric_code = self._get_intent_code_from_en_code(intent_value)
                                if numeric_code:
                                    intent_data["intent"] = numeric_code
                        return [intent_data]
            except Exception as e4:
                logger.warning(f"策略4解析失败: {str(e4)}")
                
            # 所有策略都失败
            logger.error("所有解析尝试都失败了，返回空列表")
            return []
        except Exception as e:
            logger.error(f"解析意图结果时发生严重错误: {str(e)}")
            return []
    
    async def close(self):
        """关闭MCP连接"""
        if self.mcp_client:
            try:
                # 优先尝试使用exit_stack关闭
                if hasattr(self.mcp_client, 'exit_stack'):
                    await self.mcp_client.exit_stack.aclose()
                # 如果有close方法，也调用它
                elif hasattr(self.mcp_client, 'close'):
                    await self.mcp_client.close()
                self.is_connected = False
                logger.info("MCP连接已关闭")
            except Exception as e:
                logger.error(f"关闭MCP连接时出错: {str(e)}")


# 全局实例，在需要时才初始化
global_mcp_intent_recognizer = None


def get_mcp_intent_recognizer():
    global global_mcp_intent_recognizer
    if global_mcp_intent_recognizer is None:
        global_mcp_intent_recognizer = MCPIntentRecognizer()
    return global_mcp_intent_recognizer