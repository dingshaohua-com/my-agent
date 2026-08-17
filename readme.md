这个机制在不同语境和技术体系中有几种最主流的叫法：

* **Function Calling（函数调用）**：这是最经典、最通用的行业标准术语（由 OpenAI 最先确立标准），国内外的各大模型 API（DeepSeek、Kimi、通义千问等）都沿用此名称。
* **Tool Calling / Tools（工具调用）**：随着能力扩展（不仅能调本地函数，还能调 Web 搜索、代码解释器等外部系统），当前各大 SDK（如 OpenAI、Anthropic、Gemini）在入参参数名上均已统称为 `tools`。
* **ReAct（Reason + Act，推理行动模式）**：学术界和 Agent 架构设计中，将“思考 $\rightarrow$ 决定调工具 $\rightarrow$ 获取反馈 $\rightarrow$ 继续思考”的这种闭环工作流范式称为 **ReAct 模式**。
* **MCP（Model Context Protocol）**：如果你使用的是标准化的外部插件/服务协议（如 Anthropic 开源的标准），这类标准化工具服务被称为 **MCP Tools / MCP Servers**。