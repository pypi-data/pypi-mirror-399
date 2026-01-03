# -*- coding: utf-8 -*-
"""简易版fastmcp模块实现，提供基础的Client类"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Client:
    """简易版MCP客户端实现"""
    
    def __init__(self, url: str = None):
        self.server_url = url if url else None
        self.session = None
        self.exit_stack = None
        logger.info("FastMCP Client 已初始化")
    
    async def connect(self, url: str = None) -> bool:
        """连接到MCP服务器"""
        try:
            # 如果提供了URL，更新服务器地址
            if url:
                self.server_url = url
            elif not self.server_url:
                # 如果没有提供URL且没有默认URL，则使用一个默认值
                self.server_url = "http://127.0.0.1:8000/mcp"
            
            self.session = aiohttp.ClientSession()
            logger.info(f"成功连接到MCP服务器: {self.server_url}")
            return True
        except Exception as e:
            logger.error(f"连接MCP服务器失败: {str(e)}")
            return False
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        try:
            # 这里返回一个模拟的工具列表，包含intent_recognizer工具
            tools = [
                {
                    "name": "recognize_intent",
                    "description": "识别用户输入中的意图",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_input": {
                                "type": "string",
                                "description": "用户输入的文本内容"
                            }
                        },
                        "required": ["user_input"]
                    }
                }
            ]
            
            # 转换为特定格式
            formatted_tools = []
            for tool in tools:
                formatted_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                })
            
            return formatted_tools
        except Exception as e:
            logger.error(f"获取工具列表失败: {str(e)}")
            return []
    
    async def call_tool(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """调用MCP工具"""
        try:
            # 模拟工具调用响应
            responses = []
            
            # 处理每个工具调用
            for tool_call in tool_calls:
                # 提取函数名和参数（支持不同格式）
                if isinstance(tool_call, dict):
                    function_name = tool_call.get("function", {}).get("name")
                    arguments = tool_call.get("function", {}).get("arguments")
                else:
                    # 如果是对象格式
                    function_name = getattr(tool_call, "function", None)
                    if function_name:
                        function_name = getattr(function_name, "name", None)
                    arguments = getattr(tool_call, "function", None)
                    if arguments:
                        arguments = getattr(arguments, "arguments", None)
                
                if function_name == "recognize_intent" and arguments:
                    try:
                        # 解析参数
                        if isinstance(arguments, str):
                            args_dict = json.loads(arguments)
                        else:
                            args_dict = arguments
                        
                        user_input = args_dict.get("user_input", "")
                        print(f"[MCP] 识别意图: '{user_input}'")
                        
                        # 简单的意图识别逻辑（基于关键词）
                        intent_result = await self._simple_intent_recognizer(user_input)
                        print(f"[MCP] 识别结果: {intent_result}")
                        
                        # 添加工具调用结果
                        responses.append({
                            "role": "tool",
                            "content": json.dumps(intent_result, ensure_ascii=False)
                        })
                    except Exception as e:
                        print(f"[MCP] 处理意图识别时出错: {str(e)}")
                        responses.append({
                            "role": "tool",
                            "content": "[]"
                        })
            
            # 如果没有工具响应，返回空结果
            if not responses:
                responses.append({
                    "role": "tool",
                    "content": "[]"
                })
            
            return responses
        except Exception as e:
            logger.error(f"调用工具失败: {str(e)}")
            # 返回错误响应
            return [
                {"role": "system", "content": "Error processing tool call"},
                {"role": "tool", "content": "[]"}
            ]
    
    async def _simple_intent_recognizer(self, user_input: str) -> List[Dict[str, Any]]:
        """改进的基于关键词的意图识别实现 - 灵活支持各种带参数的意图"""
        import re
        # 导入全局意图映射
        try:
            from . import ai_llm
            global_intents = ai_llm.gLOBAL_INTENTS
            logger.info(f"获取到的全局意图映射: {global_intents}")
        except ImportError:
            logger.error("无法导入ai_llm模块，使用空意图映射")
            global_intents = {}
        except AttributeError:
            logger.error("ai_llm模块中未找到gLOBAL_INTENTS，使用空意图映射")
            global_intents = {}
        
        intents = []
        user_input_lower = user_input.lower()
        
        # 将输入文本按逻辑分隔符分割成多个子句，保持意图顺序
        # 分隔符包括：然后、并且、接着、再、先...然后
        split_patterns = [r'[然后并且接着再]', r'先.*?然后']
        clauses = [user_input_lower]
        
        for pattern in split_patterns:
            new_clauses = []
            for clause in clauses:
                # 使用正则表达式分割，保留分隔符以便后续处理
                parts = re.split(f'({pattern})', clause)
                temp_clauses = []
                for i, part in enumerate(parts):
                    if part:
                        temp_clauses.append(part)
                new_clauses.extend(temp_clauses)
            clauses = new_clauses
        
        # 清理子句，移除空白和分隔符
        cleaned_clauses = []
        for clause in clauses:
            # 移除分隔符
            clause = re.sub(r'[然后并且接着再先]', '', clause)
            # 移除空白字符
            clause = clause.strip()
            if clause:  # 只保留非空的子句
                cleaned_clauses.append(clause)
        
        # 如果没有分割出子句，使用原始输入
        if not cleaned_clauses:
            cleaned_clauses.append(user_input_lower)
        
        # 对每个子句独立进行意图识别，保持顺序
        for clause in cleaned_clauses:
            # 遍历所有全局意图，检查每个意图的关键词是否在子句中出现
            for intent_code, intent_info in global_intents.items():
                keywords = intent_info.get("keywords", [])
                matched = False
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    # 1. 精确匹配
                    if keyword_lower == clause:
                        matched = True
                        break
                    
                    # 2. 包含匹配（关键词是子句的一部分）
                    if keyword_lower in clause:
                        matched = True
                        break
                    
                    # 3. 语义相似匹配（关键词的核心词汇出现在子句中）
                    # 提取关键词中的核心词汇（去掉修饰词）
                    keyword_core = re.sub(r'[调节到了]', '', keyword_lower)
                    if keyword_core and keyword_core in clause:
                        matched = True
                        break
                
                if matched:
                    # 提取参数 - 只从当前子句中提取与该意图相关的参数
                    args = []
                    
                    # 尝试从子句中提取数字作为参数（支持整数、小数和百分比）
                    # 匹配模式：数字（可能带小数点）后跟可选的单位
                    number_patterns = [
                        r'\d+(?:\.\d+)?',  # 匹配整数和小数
                        r'\d+(?:\.\d+)?%'  # 匹配百分比
                    ]
                    
                    for pattern in number_patterns:
                        numbers = re.findall(pattern, clause)
                        if numbers:
                            # 提取第一个数字作为主要参数
                            args.append(numbers[0].replace('%', ''))  # 移除百分号
                            break
                    
                    intents.append({
                        "intent": str(intent_code),  # 将数字代码转换为字符串，与传统意图识别保持一致
                        "arg": args  # 返回提取的参数
                    })
        
        # 去重 - 避免同一子句中同一意图被多次识别（但允许不同子句中识别相同意图）
        unique_intents = []
        seen_in_clauses = []  # 记录已经在哪些子句中识别了哪些意图
        for i, clause in enumerate(cleaned_clauses):
            clause_intents = []
            clause_seen = set()
            
            for intent in intents:
                # 检查这个意图是否来自当前子句
                # 由于我们没有直接记录意图来自哪个子句，这里使用一个近似的方法
                # 检查意图的关键词是否在当前子句中出现
                intent_code = int(intent["intent"])
                intent_info = global_intents.get(intent_code, {})
                keywords = intent_info.get("keywords", [])
                
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in clause or re.sub(r'[调节到了]', '', keyword_lower) in clause:
                        # 这个意图可能来自当前子句
                        if intent["intent"] not in clause_seen:
                            clause_seen.add(intent["intent"])
                            clause_intents.append(intent)
                        break
            
            seen_in_clauses.extend(clause_intents)
        
        # 最终的意图列表是按子句顺序排列的去重后的意图
        return seen_in_clauses
    
    async def close(self):
        """关闭MCP客户端连接和会话"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.connected = False
            logger.info("MCP客户端连接已关闭")
        except Exception as e:
            logger.error(f"关闭MCP客户端连接时出错: {str(e)}")
            # 确保即使出错也设置为未连接状态
            self.connected = False
            self.session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 为了兼容原有的exit_stack使用方式
class AsyncExitStack:
    """简易的异步退出栈实现"""
    
    def __init__(self):
        self._exit_callbacks = []
    
    async def aclose(self):
        """关闭并执行所有退出回调"""
        for callback in reversed(self._exit_callbacks):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"执行退出回调时出错: {str(e)}")
    
    def push(self, callback):
        """添加退出回调"""
        self._exit_callbacks.append(callback)
        return callback


# 为Client类添加exit_stack属性
async def create_client(url: str = None):
    """创建并初始化MCP客户端"""
    client = Client(url)
    client.exit_stack = AsyncExitStack()
    client.exit_stack.push(client.close)
    # 总是调用connect以确保会话被创建
    await client.connect()
    return client