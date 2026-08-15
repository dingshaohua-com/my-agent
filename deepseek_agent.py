import os
import dotenv
import httpx
import json
dotenv.load_dotenv()

class Deepseek:
    api_key = os.getenv('API_KEY')

    @classmethod
    def http_request(cls, msg):
        print(type(msg))
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {cls.api_key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": msg, "stream": False}
            )
            return response

    @classmethod
    def talk(cls, msg):
        response = cls.http_request(msg)
        result = response.json()
        return result["choices"][0]["message"]["content"]


class Agent:
    sysPrompt=os.getenv('SYS_PROMPT')
    historyFile = os.getenv('HISTORY_FILE')
    messages=[]

    @classmethod
    def load_history(cls):
        assert cls.historyFile is not None
        with open(cls.historyFile, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    @classmethod
    def save_history(cls, msg: list):
        assert cls.historyFile is not None
        with open(cls.historyFile, "w", encoding="utf-8") as f:
            json.dump(msg, f, ensure_ascii=False, indent=2)

    @classmethod
    def start(cls):
        cls.messages=cls.load_history()
        if not cls.messages:
            cls.messages.append({"role": "system", "content": cls.sysPrompt})
        while True:
            try:
                user_input = input("\n👤 你: ").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    print("退出对话")
                    break

                if user_input.lower() == "clear":
                    messages = [{"role": "system", "content": cls.sysPrompt}]
                    cls.save_history(messages)
                    print("🧹 本地历史记录已清空")
                    continue

                cls.messages.append({"role": "user", "content": user_input})
                result=Deepseek.talk(cls.messages)
                print("\n🤖: "+result)

                cls.messages.append({"role": "assistant", "content": result})
                cls.save_history(cls.messages)


            except KeyboardInterrupt:
                print("\n强制退出")
                break





