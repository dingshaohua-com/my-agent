这个机制在不同语境和技术体系中有几种最主流的叫法：

* **Function Calling（函数调用）**：这是最经典、最通用的行业标准术语（由 OpenAI 最先确立标准），国内外的各大模型 API（DeepSeek、Kimi、通义千问等）都沿用此名称。
* **Tool Calling / Tools（工具调用）**：随着能力扩展（不仅能调本地函数，还能调 Web 搜索、代码解释器等外部系统），当前各大 SDK（如 OpenAI、Anthropic、Gemini）在入参参数名上均已统称为 `tools`。
* **ReAct（Reason + Act，推理行动模式）**：学术界和 Agent 架构设计中，将“思考 $\rightarrow$ 决定调工具 $\rightarrow$ 获取反馈 $\rightarrow$ 继续思考”的这种闭环工作流范式称为 **ReAct 模式**。
* **MCP（Model Context Protocol）**：如果你使用的是标准化的外部插件/服务协议（如 Anthropic 开源的标准），这类标准化工具服务被称为 **MCP Tools / MCP Servers**。


你当前是通过「原生 Function Calling / Tool Calling + ReAct 循环」给 Agent 赋能，并没有使用 MCP 协议。

判断依据：

- [deepseek.py](/Users/admin/files.localized/mcode/my-agent/deepseek.py) 直接把 `funs.TOOLS_SCHEMA` 作为 `tools` 参数传给 DeepSeek API。
- [agent.py](/Users/admin/files.localized/mcode/my-agent/agent.py) 收到 `tool_calls` 后，通过 `AVAILABLE_TOOLS` 查找并执行本地 Python 函数。
- [funs/__init__.py](/Users/admin/files.localized/mcode/my-agent/funs/__init__.py) 手工注册了两个本地工具：
  - `get_current_time`
  - `get_baidu_hot_search`
- 项目没有 MCP Client、MCP Server、JSON-RPC、stdio/SSE/Streamable HTTP 连接或 MCP SDK 依赖。

当前结构是：

```text
用户
  → DeepSeek API
  → 模型生成 tool_calls
  → Agent 查 AVAILABLE_TOOLS
  → 执行本地 Python 函数
  → 结果回传模型
  → 模型继续回答
```

所以更准确的说法是：

> 这是一个使用 DeepSeek Tool Calling、由本地 Python 工具扩展能力的 ReAct Agent。

如果改成 MCP，通常会变成：

```text
Agent（MCP Client）
  → 连接一个或多个 MCP Server
  → 自动发现 tools/list
  → 调用 tools/call
  → MCP Server 执行工具
```

你在 [readme.md](/Users/admin/files.localized/mcode/my-agent/readme.md) 中对 MCP 的解释基本正确，但它只是概念说明，项目代码目前并未实现 MCP。