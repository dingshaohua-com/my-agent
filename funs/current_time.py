from datetime import datetime
# Function Calling
# ==================== 1. 定义工具与 Schema ====================

def get_current_time() -> str:
    """获取本地当前的日期、时间和星期"""
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    weekday_str = weekdays[now.weekday()]
    return now.strftime(f"%Y年%m月%d日 %H:%M:%S {weekday_str}")


TOOL_SCHEMA = {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前系统的精确日期、时间和星期几。当用户询问现在几点、今天几号、星期几或需要基于当前时间计算时调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {},  # 该工具无需入参
                "required": []
            }
        }
}
