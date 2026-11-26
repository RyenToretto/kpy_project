# `04_all_in_rag` | RAG 技术全栈：从切块到评测

- **来源**: [datawhalechina/all-in-rag](https://github.com/datawhalechina/all-in-rag)（推荐度排名 3）
- **学习目标**: 理解 RAG 的完整链路：数据准备 -> 索引构建 -> 检索优化 -> 生成 -> 评估，并能自己写出可测的最小实现。
- **前置语法**: `list`、`dict`、`Counter`、`re` 正则、`math`
- **环境**: 本目录脚本只用标准库，不依赖向量库和 API Key；真正的 Milvus、Embedding 实战请对照原仓库。
- **许可说明**: 原仓库许可以其 `LICENSE` 为准。本目录脚本为自写的简化实现，仅供个人学习。

## 章节映射与进度

| 编号 | 原仓库章节 | 本地文件 | 核心点 | 状态 |
| --- | --- | --- | --- | --- |
| `00_` | 第二章 数据准备（文本分块） | [00_data_prep/00_text_chunking.py](./00_data_prep/00_text_chunking.py) | 定长重叠分块 vs 按句子打包 | ✅ 已完成 |
| `01_` | 第四章 检索优化（混合检索） | [01_retrieval/00_hybrid_retrieval.py](./01_retrieval/00_hybrid_retrieval.py) | BM25 + 向量相似度 + RRF 融合 | ✅ 已完成 |
| `02_` | 第六章 RAG 系统评估 | [02_evaluation/00_retrieval_metrics.py](./02_evaluation/00_retrieval_metrics.py) | Recall@K、MRR、命中率 | ✅ 已完成 |
| `03_` | 第三章 索引构建（向量嵌入、向量库） | 可用 `py-study-generator` 按需生成 | 需要 Embedding 与 Milvus，建议先装依赖 | 📝 待生成 |
| `04_` | 第四章 Text2SQL、查询重构 | 可用 `py-study-generator` 按需生成 | 自然语言转 SQL（可配合 `01_python_100_days` 的 SQLite） | 📝 待生成 |
| `05_` | 第八章 项目实战一 | 可用 `py-study-generator` 按需生成 | 把前面模块串成可上线应用 | 📝 待生成 |

**本目录总题数：6**（已完成 3，待生成 3）

## 验证

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 04_all_in_rag
```
