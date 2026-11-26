# 11_rag_techniques | RAG 进阶技巧（阶段 6 · 深挖与长期）

- **原仓库**: [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques)（42+ 个可运行的 RAG 进阶技巧案例，多为 Notebook）
- **学习阶段**: 第 6 阶段（先完成 `04_all_in_rag` 的基础 RAG 流程，再学本目录的优化手段）
- **前置语法**: `04_all_in_rag` 的切块与检索、`03_llm_universe` 的知识库问答流程
- **许可提醒**: 原仓库使用自定义的非商业许可，**商用前请先阅读其 LICENSE**。本目录脚本是自行重写的离线学习版，不包含原仓库代码。
- **为什么学它（通向接单与面试）**: 企业落地最难的不是调通一个 API，而是“搜不准、幻觉多”。学透切块、改写、重排与评估，能拉开面试与报价的差距。

## 依赖

只用 Python 标准库，**不需要 API Key、不需要向量库、不需要 GPU**。

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应技巧 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_chunking/` | Chunking 切块 | 递归分隔符切块、固定重叠、语义断点切块 | `00_recursive_chunking.py` | ✅ |
| 01 | `01_query_transform/` | Query Transformations | HyDE 假设答案检索、多查询扩展、RRF 排名融合 | `00_hyde_multi_query.py` | ✅ |
| 02 | `02_rerank/` | Reranking | 两阶段检索、精排打分、MMR 去冗余 | `00_rerank_mmr.py` | ✅ |
| 03 | `03_evaluation/` | Evaluation | 上下文召回、答案忠实度（精确/模糊）、答案相关性 | `00_rag_metrics.py` | ✅ |

## 学习循环

1. 先读脚本顶部 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 按顺序运行：切块 -> 查询改写 -> 重排 -> 评估。每一步都是 RAG 流水线的一个环节。
3. 把 `DOCS`、`CANDIDATES`、`CONTEXTS` 换成你自己的数据，观察指标变化。
4. 合上脚本，凭记忆重写一遍。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 11_rag_techniques
```
