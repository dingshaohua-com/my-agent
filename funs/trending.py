import json
import httpx


def get_baidu_hot_search(top_n: int = 10) -> str:
    """
    通过直接 JSON 接口获取百度实时热搜
    """
    url = "https://top.baidu.com/api/board?platform=pc&tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://top.baidu.com/board?tab=realtime"
    }

    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code != 200:
                return f"接口请求失败: HTTP {resp.status_code}"

            data = resp.json()
            # 提取热搜数据列表
            raw_cards = data.get("data", {}).get("cards", [])
            if not raw_cards:
                return "未获取到热搜列表数据"

            content_list = raw_cards[0].get("content", [])

            results = []
            for idx, item in enumerate(content_list[:top_n], start=1):
                results.append({
                    "rank": idx,
                    "title": item.get("word", ""),
                    "heat": item.get("hotScore", "0"),
                    "desc": item.get("desc", ""),
                    "url": item.get("rawUrl", "")
                })

            return json.dumps(results, ensure_ascii=False)

    except Exception as e:
        return f"获取热搜异常: {str(e)}"

TOOL_SCHEMA =  {
        "type": "function",
        "function": {
            "name": "get_baidu_hot_search",
            "description": "获取实时热搜排行榜（实时热点新闻与话题）。当用户询问当前热点事件、最近发生了什么、网络热议话题或百度热搜榜时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {
                        "type": "integer",
                        "description": "需要获取的热搜条数，范围 1 到 30，默认为 10"
                    }
                },
                "required": []
            }
        }
    }
