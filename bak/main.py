import httpx

url="https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY=""
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}
payload={
    "model": "deepseek-v4-pro",
    "messages": [
        {"role": "system", "content": "你是一个严谨的助手。"},
        {"role": "user", "content": "你好，用一句话介绍你自己。"}
    ],
    "thinking": {"type": "enabled"},
    "reasoning_effort": "high",
    "stream": False
}

response = httpx.post(url=url, headers=headers, json=payload)
result = response.json()
print(result["choices"][0]["message"]["content"])