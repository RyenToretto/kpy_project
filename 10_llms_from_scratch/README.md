# 10_llms_from_scratch | 从零手写类 GPT 模型（阶段 6 · 深挖原理）

- **原仓库**: [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch)（Sebastian Raschka 的配套代码，公认代码最干净的 LLM 底层仓库）
- **学习阶段**: 第 6 阶段（建议在 `09_happy_llm` 之后学习，两者互补：09 讲原理，10 讲实现）
- **前置语法**: `00_basic` 语法主线、`09_happy_llm` 的注意力与 softmax、NumPy 数组运算
- **为什么学它（通向模型开发与底层工程）**: 从分词、训练到前向，一条链路完整走一遍，能真正看懂“模型到底在算什么”，是从调包转向模型工程的关键一步。

## 版权与写法说明

本目录的脚本**不是**原仓库代码的拷贝，而是用 NumPy 重新实现的学习版，规模缩小到能在笔记本上秒级运行。原仓库使用 PyTorch 与真实数据集，学习路线请以原仓库为准。

## 依赖

只需 NumPy（项目 `.venv` 已安装）。本目录不需要 GPU、不需要下载数据集。

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应原书章节 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_tokenizer/` | 第 2 章 文本数据处理 | 字节级 BPE 训练、编码、解码、往返一致性 | `00_bpe_tokenizer.py` | ✅ |
| 01 | `01_bigram_lm/` | 第 3~4 章 训练语言模型 | 交叉熵、手写梯度、梯度下降训练、采样生成 | `00_bigram_train.py` | ✅ |
| 02 | `02_mini_gpt/` | 第 3~4 章 实现类 GPT | Embedding、因果自注意力、MLP、残差与 LayerNorm、输出头 | `00_mini_gpt_forward.py` | ✅ |

## 学习循环

1. 先读脚本顶部 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 按顺序运行：分词 -> Bigram 训练 -> 迷你 GPT 前向。
3. 把 `01_bigram_lm` 的语料换成你自己的文本，观察生成效果。
4. 合上脚本，凭记忆重写一遍（尤其是 BPE 的合并与 GPT 的前向）。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 10_llms_from_scratch
```
