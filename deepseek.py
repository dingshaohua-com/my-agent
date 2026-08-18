import os
import httpx

class Deepseek:
    api_key = os.getenv('API_KEY')
    tools_schema=[]

    @classmethod
    def register_tools(cls, tools_schema):
        cls.tools_schema.extend(tools_schema)

    @classmethod
    def http_request(cls, msg):
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                "https://api.deepseek.com/chat/completions",
                headers={"Authorization": f"Bearer {cls.api_key}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": msg, "stream": False, "tool_choice":"auto", "tools":cls.tools_schema}
            )
            return response

    @classmethod
    def talk(cls, msg):
        response = cls.http_request(msg)
        result = response.json()
        return result["choices"][0]["message"]
