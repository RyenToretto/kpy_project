# 03_llm_universe | 大模型应用开发入门（阶段 3 · LLM 应用与 RAG）

- **原仓库**: [datawhalechina/llm-universe](https://github.com/datawhalechina/llm-universe)（面向小白的大模型应用开发教程）
- **学习阶段**: 第 3 阶段（先学本目录，再学 `04_all_in_rag` 的检索细节）
- **前置语法**: `00_basic` 语法主线、`02_pydata_book` 的字符串与列表处理
- **为什么学它（通向 AI 副业 / 知识库产品）**: 门槛最低的大模型应用入门，几天就能做出第一个“能回答自己文档”的知识库 Demo。

## 版权与写法说明

本目录的脚本**不是**原教程代码的拷贝，而是按知识点用自己的话重写的学习版。为了做到离线可运行，**大模型调用用规则版假模型代替**，接口形态与真实 API 一致。

## 接入真实大模型（可选）

1. 在服务商控制台申请 API Key（不要提交到代码仓库）。
2. 设置环境变量，例如 `export DEMO_LLM_API_KEY=你的密钥`。
3. 把 `01_knowledge_base_qa/00_keyword_rag.py` 中的 `fake_llm` 换成真实的 chat 接口调用，输入仍是 `build_context_prompt` 生成的文本。

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应原教程 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_llm_api_basics/` | 第 1~2 章 API 与 Prompt | messages 角色、Prompt 模板、Token 估算、密钥环境变量 | `00_prompt_and_messages.py` | ✅ |
| 01 | `01_knowledge_base_qa/` | 第 3~4 章 知识库助手 | 文档切块、关键词检索、上下文拼接、带引用回答 | `00_keyword_rag.py` | ✅ |
| 02 | `02_chat_app_state/` | 第 5 章 Web 应用 | 会话历史、滑动窗口裁剪、清空会话 | `00_chat_history.py` | ✅ |

## 学习循环

1. 先读脚本顶部 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 运行一次：`.venv/bin/python 03_llm_universe/01_knowledge_base_qa/00_keyword_rag.py`。
3. 往 `DOCS` 里加入你自己的文档，观察检索结果与引用是否合理。
4. 合上脚本，凭记忆重写一遍。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 03_llm_universe
```
