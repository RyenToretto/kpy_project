# 06_mcp_beginners | MCP 入门（阶段 4 · Agent 与 MCP）

- **原仓库**: [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners)（微软官方 MCP 入门课程）
- **学习阶段**: 第 4 阶段（配合 `05_hello_agents` 学习，先会写 Agent，再学怎么把工具标准化）
- **前置语法**: `00_basic` 语法主线、`01_python_100_days` 的 JSON 与异常处理、装饰器与 dataclass
- **为什么学它（通向 AI 提效与接单）**: Cursor、Claude 等 Agent 生态重度依赖 MCP。学会自写 MCP Server，就能把企业内部的数据库、文档、业务接口接入任何 Agent。

## 版权与写法说明

本目录的脚本**不是**原课程代码的拷贝，而是按协议知识点用标准库重写的学习版，**不依赖官方 `mcp` SDK**，离线即可运行，方便你看清消息流转的每一步。真正上线时，建议改用官方 SDK。

## 学习路线

先理解协议消息（JSON-RPC），再写服务端（注册工具、响应请求），最后写客户端（握手、发现、调用）。三步对应真实 MCP 的三个角色。

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应原课程 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_jsonrpc_basics/` | 第 1 章 MCP 基础概念 | JSON-RPC 请求/响应/通知、错误码 | `00_jsonrpc_messages.py` | ✅ |
| 01 | `01_tool_server/` | 第 2~3 章 构建 Server | 工具注册、`initialize`、`tools/list`、`tools/call`、参数校验 | `00_mini_mcp_server.py` | ✅ |
| 02 | `02_client_session/` | 第 4 章 客户端与会话 | 握手流程、请求 id 匹配、错误转异常、未握手保护 | `00_mini_mcp_client.py` | ✅ |

## 学习循环

1. 先读脚本顶部 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 按顺序运行：`.venv/bin/python 06_mcp_beginners/01_tool_server/00_mini_mcp_server.py`。
3. 在服务端里新增一个工具（比如 `multiply`），再用客户端调用它。
4. 合上脚本，凭记忆重写一遍。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 06_mcp_beginners
```
