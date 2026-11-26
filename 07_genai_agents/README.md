# `07_genai_agents` | 生成式 AI 智能体实战案例

- **来源**: [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents)（推荐度排名 4）
- **学习目标**: 从「单个 Agent 稳定调用工具」到「多个 Agent 分工协作」，学会把案例拆成可复用的模板，用于作品集和外包。
- **前置语法**: `dict`、`json`、`dataclass`、`Callable`
- **环境**: 本目录脚本只用标准库，用规则版假 LLM 模拟模型输出，**不需要 API Key**。
- **许可说明**: 原仓库的案例请以其 `LICENSE` 为准。本目录脚本是自写的简化实现，仅供个人学习；原仓库案例目录请自行对照阅读。

## 章节映射与进度

| 编号 | 对应主题 | 本地文件 | 核心点 | 状态 |
| --- | --- | --- | --- | --- |
| `00_` | 单 Agent 工具调用 | [00_single_agent/00_tool_calling_router.py](./00_single_agent/00_tool_calling_router.py) | JSON 工具调用、参数校验、报错后自我纠正重试 | ✅ 已完成 |
| `01_` | 多 Agent 协作 | [01_multi_agent/00_pipeline_agents.py](./01_multi_agent/00_pipeline_agents.py) | 研究员 -> 写手 -> 审稿人流水线，审稿不通过则返工 | ✅ 已完成 |
| `02_` | 带记忆的对话 Agent | 可用 `py-study-generator` 按需生成 | 对话历史、摘要压缩 | 📝 待生成 |
| `03_` | 客服 / 研报等行业案例 | 可用 `py-study-generator` 按需生成 | 选 3 ~ 5 个案例改造成作品集 | 📝 待生成 |

**本目录总题数：4**（已完成 2，待生成 2）

## 验证

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 07_genai_agents
```
