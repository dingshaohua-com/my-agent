import os
import json
from pathlib import Path
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

from deepseek import Deepseek
from mcp_cfg.mcp_client import AgentMCPClient

PROJECT_DIR = Path(__file__).resolve().parent
BASE_DIR = Path(__file__).resolve().parent
MCP_DIR = BASE_DIR / "mcp_cfg"
MCP_SERVER_PATH = MCP_DIR / "mcp_server.py"

class Agent:
    sys_prompt=os.getenv('SYS_PROMPT')
    history_file = os.getenv('HISTORY_FILE')
    messages=[]
    mcp_client=None

    @classmethod
    def load_history(cls):
        assert cls.history_file is not None
        with open(cls.history_file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    @classmethod
    def save_history(cls, msg: list):
        assert cls.history_file is not None
        with open(cls.history_file, "w", encoding="utf-8") as f:
            json.dump(msg, f, ensure_ascii=False, indent=2)


    @classmethod
    async def execute_mcp_tools(cls, tool_calls):
        """
        遍历执行大模型指定的全部工具，并返回标准格式的 tool 消息列表
        """
        tool_messages = []
        for tool_call in tool_calls:
            function = tool_call["function"]
            function_name = function["name"]
            tool_call_id = tool_call["id"]
            try:
                raw_arguments = function.get("arguments") or "{}"
                arguments = json.loads(raw_arguments)
                result = await cls.mcp_client.call_tool(function_name,arguments)
                print(f"⚙️ [MCP 工具调用] {function_name}({arguments})，拿到结果{result}")
            except json.JSONDecodeError:
                result = "工具参数不是合法的 JSON"
            except Exception as exc:
                result = f"MCP 工具执行失败：{exc}"
            tool_messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": str(result),
            })
        return tool_messages

    @classmethod
    async def run_turn(cls, user_input):
        """
            处理单轮用户输入的完整思考-行动闭环
        """
        # 1. 记录用户输入
        cls.messages.append({"role": "user", "content": user_input})

        # ---设置最大重试步数，防止工具陷入死循环
        max_steps = 5
        step_count = 0

        while step_count < max_steps:
            step_count += 1
            from deepseek import Deepseek
            response = Deepseek.talk(cls.messages)

            # 存入 assistant 消息
            cls.messages.append(response)

            if not response.get("tool_calls"):
                # 记录最终回答并保存
                cls.save_history(cls.messages)
                return response.get("content","")  # 退出循环，返回最终文本

            else:
                tool_results = await cls.execute_mcp_tools(response["tool_calls"])
                cls.messages.extend(tool_results) # 把所有工具执行结果追加到上下文
                cls.save_history(cls.messages)

        # 超出最大步数限制的兜底保护
        fallback_reply = "抱歉，任务执行步数过多，已自动终止。"
        cls.messages.append({"role": "assistant", "content": fallback_reply})
        cls.save_history(cls.messages)
        return fallback_reply

    @classmethod
    async def load_mcp(cls,callback):
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                "python",
                str(MCP_SERVER_PATH),
            ],
            cwd=PROJECT_DIR,
        )
        transport = stdio_client(server_params)
        async with Client(transport) as official_client:
            mcp_client = AgentMCPClient(official_client)
            tools = await mcp_client.get_deepseek_tools()
            print(f"已连接 MCP Server，发现 {len(tools)} 个工具")
            await callback(mcp_client, tools)


    @classmethod
    async def chat_loop(cls,mcp_client, tools_schema):
        cls.mcp_client = mcp_client # 在咱们自己执行tools的时候，提供可执行对象
        Deepseek.register_tools(tools_schema) # 让deepseek知道目前有哪些tools
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    print("退出对话")
                    break

                if user_input.lower() == "clear":
                    cls.messages = []
                    cls.save_history(cls.messages)
                    print("🧹 本地历史记录已清空")
                    continue

                reply = await cls.run_turn(user_input)
                print(f"🤖：{reply}")

            except KeyboardInterrupt:
                print("\n强制退出")
                break

    @classmethod
    async def start(cls):
        cls.messages=cls.load_history()
        if not cls.messages:
            cls.messages.append({"role": "system", "content": cls.sys_prompt})
        await cls.load_mcp(cls.chat_loop)






