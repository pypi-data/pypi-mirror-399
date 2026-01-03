
import json
import sys
import os
import asyncio
from typing import Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from .mcp_fastmcp import Client, AsyncExitStack


class MCPClient:
    """MCP客户端，负责与MCP服务器通信"""

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.session = None
        
    async def connect(self, server_url: str):
        try:
            # 使用我们的简易fastmcp实现
            self.session = Client()
            await self.session.connect(server_url)
            # 模拟ping操作
            return True
        except Exception as e:
            print(f"连接MCP服务器失败: {str(e)}")
            return False

    async def get_tools(self):
        if not self.session:
            return []
        
        # 使用我们的简易实现获取工具
        try:
            tools = await self.session.get_tools()
            return tools
        except Exception as e:
            print(f"获取工具列表失败: {str(e)}")
            return []
    
    async def call_tool(self, tool_calls):
        GREEN = "\033[32m"
        RESET = "\033[0m"
        messages = []
        
        try:
            # 适配工具调用格式
            adapted_tool_calls = []
            for tool_call in tool_calls:
                # 处理不同的参数访问方式
                if hasattr(tool_call, 'function'):
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_call_id = tool_call.id
                else:
                    # 处理字典格式的工具调用
                    tool_name = tool_call.get("function", {}).get("name")
                    tool_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                    tool_call_id = tool_call.get("id", "1")
                
                print(f'\n{GREEN}调用工具: {tool_name} , 参数: {tool_args}{RESET}\n')
                
                # 构建适合我们简易实现的工具调用
                adapted_call = {
                    "id": tool_call_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(tool_args)
                    }
                }
                adapted_tool_calls.append(adapted_call)
            
            # 调用我们的简易实现
            results = await self.session.call_tool(adapted_tool_calls)
            return results
        except Exception as e:
            print(f"调用工具失败: {str(e)}")
            # 返回错误响应
            return [
                {"role": "system", "content": "Error processing tool call"},
                {"role": "tool", "content": "[]"}
            ]
            



    
if __name__ == "__main__":
    async def main():
        client = MCPClient()
        # await client.connect("http://127.0.0.1:8000/mcp")
        await client.connect("./ezai/server.py")
        print(await client.get_tools())

    
    asyncio.run(main())