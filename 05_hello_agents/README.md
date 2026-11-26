# `05_hello_agents` | 从零构建智能体

- **来源**: [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents)（推荐度排名 1）
- **学习目标**: 看懂并手写 ReAct、Reflection、Plan-and-Solve 等经典 Agent 范式，再进入框架、记忆与多智能体通信。
- **前置语法**: `00_basic/chapter04_if_elif_else`、`dict`、`re` 正则、`dataclass`
- **环境**: 本目录脚本只用标准库，**不需要 API Key**，用「规则版假 LLM」模拟模型输出，离线可跑。
- **许可说明**: 原仓库许可证为非 MIT 协议，以其 `LICENSE` 为准。本目录脚本是自写的简化实现，不是原文拷贝，仅供个人学习。

## 章节映射与进度

| 编号 | 原仓库章节 | 本地文件 | 核心点 | 状态 |
| --- | --- | --- | --- | --- |
| `00_` | 第四章 智能体经典范式构建 | [00_agent_basics/00_react_loop.py](./00_agent_basics/00_react_loop.py) | Thought / Action / Observation 循环、安全计算器工具 | ✅ 已完成 |
| `00_` | 第四章 智能体经典范式构建 | [00_agent_basics/01_reflection_loop.py](./00_agent_basics/01_reflection_loop.py) | 生成 -> 批评 -> 修订，带最大轮数与无进展保护 | ✅ 已完成 |
| `01_` | 第四章 Plan-and-Solve | [01_planning/00_plan_and_solve.py](./01_planning/00_plan_and_solve.py) | 先规划步骤，再逐步执行，`#n` 引用前序结果，失败即停止 | ✅ 已完成 |
| `02_` | 第六、七章 框架开发 | [02_framework/00_mini_state_graph.py](./02_framework/00_mini_state_graph.py) | 状态图：节点、边、条件路由、循环保护（LangGraph 思想） | ✅ 已完成 |
| `03_` | 第八、九章 记忆与上下文工程 | [03_memory_context/00_memory_and_budget.py](./03_memory_context/00_memory_and_budget.py) | 短期窗口、长期记忆检索、按优先级的上下文预算裁剪 | ✅ 已完成 |
| `04_` | 第十章 智能体通信协议 | [04_protocols/00_agent_message_bus.py](./04_protocols/00_agent_message_bus.py) | 智能体名片、消息信封、按技能发现与路由（A2A 思想，可配合 `06_mcp_beginners`） | ✅ 已完成 |

**本目录总题数：6（已完成 6，待生成 0）**

## 验证

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 05_hello_agents
```
