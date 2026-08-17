import funs.current_time as current_time
from funs import trending

# 本地可用工具映射表
AVAILABLE_TOOLS = {
    "get_current_time": current_time.get_current_time,
    "get_baidu_hot_search": trending.get_baidu_hot_search
}

# 提交给大模型的工具描述定义（标准 OpenAI 格式）
TOOLS_SCHEMA = [current_time.TOOL_SCHEMA, trending.TOOL_SCHEMA]
