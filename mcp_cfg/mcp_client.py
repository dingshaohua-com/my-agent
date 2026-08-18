import json
from typing import Any
from mcp.client import Client

class AgentMCPClient:
    def __init__(self, client: Client):
        self.client = client

    async def get_deepseek_tools(self) -> list[dict]:
        """将 MCP 工具转换成 DeepSeek Tool Calling 格式。"""
        response = await self.client.list_tools()

        tools = []

        for tool in response.tools:
            tool_data = tool.model_dump(
                mode="json",
                by_alias=True,
                exclude_none=True,
            )
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_data["name"],
                    "description": tool_data.get("description", ""),
                    "parameters": tool_data.get(
                        "inputSchema",
                        {
                            "type": "object",
                            "properties": {},
                        },
                    ),
                },
            })
        return tools

    async def call_tool(self,name,arguments):
        result = await self.client.call_tool(name,arguments)
        if result.is_error:
            raise RuntimeError(f"MCP 工具 {name} 执行失败")
        contents = []
        for content in result.content:
            if content.type == "text":
                contents.append(content.text)
            else:
                contents.append(
                    json.dumps(
                        content.model_dump(
                            mode="json",
                            by_alias=True,
                        ),
                        ensure_ascii=False,
                    )
                )

        return "\n".join(contents)