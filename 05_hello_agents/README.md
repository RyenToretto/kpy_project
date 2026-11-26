# `05_hello_agents` | 从零构建智能体

- **来源**: [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents)（推荐度排名 1）
- **学习目标**: 看懂并手写 ReAct、Reflection 等经典 Agent 范式，再进入框架、MCP、记忆与多智能体。
- **前置语法**: `chapter04_if_elif_else`、`dict`、`re` 正则、`dataclass`
- **环境**: 本目录脚本只用标准库，**不需要 API Key**，用「规则版假 LLM」模拟模型输出，离线可跑。
- **许可说明**: 原仓库许可证为非 MIT 协议，以其 `LICENSE` 为准。本目录脚本是自写的简化实现，不是原文拷贝，仅供个人学习。

## 章节映射与进度

| 编号 | 原仓库章节 | 本地文件 | 核心点 | 状态 |
| --- | --- | --- | --- | --- |
| `00_` | 第四章 智能体经典范式构建 | [00_agent_basics/00_react_loop.py](./00_agent_basics/00_react_loop.py) | Thought / Action / Observation 循环、安全计算器工具 | ✅ 已完成 |
| `01_` | 第四章 智能体经典范式构建 | [00_agent_basics/01_reflection_loop.py](./00_agent_basics/01_reflection_loop.py) | 生成 -> 批评 -> 修订，带最大轮数与无进展保护 | ✅ 已完成 |
| `02_` | 第四章 Plan-and-Solve | 可用 `py-study-generator` 按需生成 | 先规划步骤再逐步执行 | 📝 待生成 |
| `03_` | 第六、七章 框架开发 | 可用 `py-study-generator` 按需生成 | LangGraph / 自研框架 | 📝 待生成 |
| `04_` | 第八、九章 记忆与上下文工程 | 可用 `py-study-generator` 按需生成 | 记忆系统、上下文裁剪 | 📝 待生成 |
| `05_` | 第十章 智能体通信协议 | 可用 `py-study-generator` 按需生成 | MCP / A2A（可配合 `06_mcp_beginners`） | 📝 待生成 |

**本目录总题数：6**（已完成 2，待生成 4）

## 验证

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 05_hello_agents
```
