import json
import httpx
from datetime import datetime
from mcp.server import MCPServer

from funs.current_time import get_current_time as current_time_impl
from funs.trending import get_baidu_hot_search as hot_search_impl

mcp = MCPServer("my-agent-tools")


@mcp.tool()
def get_current_time() -> str:
    """获取本地当前的日期、时间和星期"""
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_str = weekdays[now.weekday()]
    return now.strftime(f"%Y年%m月%d日 %H:%M:%S {weekday_str}")

@mcp.tool()
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

if __name__ == "__main__":
    mcp.run()