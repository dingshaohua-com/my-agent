import os
import dotenv
import httpx
import json
import funs

dotenv.load_dotenv()

class Deepseek:
    api_key = os.getenv('API_KEY')

    @classmethod
    def http_request(cls, msg):
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {cls.api_key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": msg, "stream": False, "tool_choice":"auto", "tools":funs.TOOLS_SCHEMA}
            )
            return response

    @classmethod
    def talk(cls, msg):
        response = cls.http_request(msg)
        result = response.json()
        return result["choices"][0]["message"]


class Agent:
    sys_prompt=os.getenv('SYS_PROMPT')
    history_file = os.getenv('HISTORY_FILE')
    messages=[]

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
    def execute_fun(cls, tool_calls):
        """
        遍历执行大模型指定的全部工具，并返回标准格式的 tool 消息列表
        """
        tool_messages = []

        for tool_call in tool_calls:
            func_name = tool_call["function"]["name"]
            tool_call_id = tool_call["id"]

            # 1. 容错解析参数（防止模型偶发吐出不合法 JSON）
            try:
                raw_args = tool_call["function"].get("arguments") or "{}"
                func_args = json.loads(raw_args)
            except json.JSONDecodeError:
                func_args = {}

            print(f"  ⚙️ [Agent 执行工具] -> {func_name}({func_args})")

            # 2. 匹配并执行本地函数
            if func_name in funs.AVAILABLE_TOOLS:
                tool_func = funs.AVAILABLE_TOOLS[func_name]
                try:
                    tool_result = tool_func(**func_args)
                except Exception as e:
                    tool_result = f"工具执行异常: {str(e)}"
            else:
                tool_result = f"错误：未找到名为 {func_name} 的工具"

            # 3. 统一序列化为字符串（字典/列表优先转 json 格式）
            if isinstance(tool_result, (dict, list)):
                content = json.dumps(tool_result, ensure_ascii=False)
            else:
                content = str(tool_result)

            # 4. 存入结果列表
            tool_messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": content
            })

        return tool_messages

    @classmethod
    def run_turn(cls, user_input):
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
            response = Deepseek.talk(cls.messages)

            # 存入 assistant 消息
            cls.messages.append(response)

            if not response.get("tool_calls"):
                # 记录最终回答并保存
                cls.save_history(cls.messages)
                return response.get("content","")  # 退出循环，返回最终文本

            else:
                tool_results = cls.execute_fun(response["tool_calls"]) # 批量执行工具
                cls.messages.extend(tool_results) # 把所有工具执行结果追加到上下文
                cls.save_history(cls.messages)

        # 超出最大步数限制的兜底保护
        fallback_reply = "抱歉，任务执行步数过多，已自动终止。"
        cls.messages.append({"role": "assistant", "content": fallback_reply})
        cls.save_history(cls.messages)
        return fallback_reply

    @classmethod
    def start(cls):
        cls.messages=cls.load_history()
        if not cls.messages:
            cls.messages.append({"role": "system", "content": cls.sys_prompt})
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

                reply = cls.run_turn(user_input)
                print(reply)

            except KeyboardInterrupt:
                print("\n强制退出")
                break





