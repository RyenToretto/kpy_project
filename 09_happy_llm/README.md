# 09_happy_llm | 从零开始的大模型（阶段 6 · 深挖原理）

- **原仓库**: [datawhalechina/happy-llm](https://github.com/datawhalechina/happy-llm)（中文系统性大模型教材）
- **学习阶段**: 第 6 阶段（想真正看懂模型原理时再学，建议先完成阶段 3 ~ 5）
- **前置语法**: `02_pydata_book/00_numpy_basics`（ndarray 与广播）、矩阵乘法、三角函数基础
- **为什么学它（通向大模型岗位与微调）**: 面大模型应用或微调岗位时，Attention、KV Cache、RoPE、LoRA 是高频面试与工作话题，这些代码能直接解释“为什么推理慢”“为什么显存不够”。

## 版权与写法说明

本目录的脚本**不是**原教材代码的拷贝，而是按章节知识点用 NumPy 重写的学习版，每个脚本都用**数学性质**做断言（例如“KV Cache 结果与整段重算一致”“RoPE 只依赖相对位置”），不依赖 GPU 与模型权重。

## 依赖

只需 NumPy（项目 `.venv` 已安装）：

```bash
.venv/bin/python -m pip install numpy
```

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应原教材 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_attention_basics/` | 第 2 章 Transformer 架构 | 缩放点积注意力、softmax 数值稳定、因果掩码 | `00_scaled_dot_product_attention.py` | ✅ |
| 01 | `01_multi_head_kv_cache/` | 第 2~3 章 多头与推理加速 | 多头拆分合并、KV Cache 增量解码、因果性验证 | `00_multi_head_kv_cache.py` | ✅ |
| 02 | `02_norm_and_rope/` | 第 2 章 位置编码与归一化 | RMSNorm、LayerNorm 对比、RoPE 旋转、相对位置性质 | `00_rmsnorm_rope.py` | ✅ |
| 03 | `03_lora_finetune/` | 第 5 章 大模型微调 | LoRA 低秩分解、零初始化、权重合并、参数量对比 | `00_lora_low_rank.py` | ✅ |

## 学习循环

1. 先读脚本顶部 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 运行一次：`.venv/bin/python 09_happy_llm/01_multi_head_kv_cache/00_multi_head_kv_cache.py`。
3. 改动 `seq_len` 或 `n_heads`，观察断言是否仍然成立。
4. 合上脚本，凭记忆重写一遍（尤其是 KV Cache 与 RoPE 的公式）。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 09_happy_llm
```
