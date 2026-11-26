"""
[主题]: 缩放点积注意力 (Scaled Dot-Product Attention) 与因果掩码 (Causal Mask)
[来源]: datawhalechina/happy-llm 第 2 章「Transformer 架构」(本文件为自行重写的 NumPy 学习版)
[难度]: Medium
[前置知识]: 02_pydata_book/00_numpy_basics (ndarray、广播)、矩阵乘法、softmax 的概念

一、主题说明
注意力回答一个问题：处理第 i 个词时，应该“看”序列里的哪些词，各看多少？
- Q (query): 我在找什么；K (key): 每个词能提供什么标签；V (value): 每个词真正携带的内容。
- 分数 = Q·K^T / sqrt(d_k)，除以 sqrt(d_k) 是为了防止点积过大导致 softmax 饱和。
- 权重 = softmax(分数)，输出 = 权重 · V。
- 因果掩码: 语言模型只能看见过去，未来位置的分数被设为 -inf，softmax 后权重为 0。

二、解法对比（以「对每个位置单独算注意力」为例）
1. 直观版 attention_loop: 双重 for 循环，逐个位置计算分数与加权和。
   - 时间复杂度 O(T^2 * d)，但每一步都能清楚对应公式。
2. 进阶版 attention: 用矩阵乘法一次算完所有位置。
   - 时间复杂度 O(T^2 * d)（计算量相同），但利用 BLAS 加速，速度快得多，代码也更短。
   - 空间复杂度 O(T^2)：注意力矩阵本身就是 T×T，这也是长上下文昂贵的根源。

三、真实用途
- 大数据: 长文本与日志建模时，注意力的 O(T^2) 开销决定了上下文长度上限。
- 数据分析: 时间序列预测（如 Transformer 预测销量）同样用这套注意力。
- AI Agent / RAG: 模型“读”检索到的资料，本质是对这些段落做注意力加权。
- 全栈开发: 推理服务的延迟与显存占用，直接由注意力矩阵大小决定，理解它有助于性能优化。
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def softmax(scores: FloatArray, axis: int = -1) -> FloatArray:
    """数值稳定的 softmax：先减去最大值，避免 exp 溢出；-inf 会变成 0。"""
    shifted = scores - np.max(scores, axis=axis, keepdims=True)
    exp_scores = np.exp(shifted)
    return exp_scores / np.sum(exp_scores, axis=axis, keepdims=True)


def attention_loop(q: FloatArray, k: FloatArray, v: FloatArray) -> FloatArray:
    """直观版：逐个查询位置计算权重，再对 V 加权求和。"""
    seq_len, d_k = q.shape
    output = np.zeros((seq_len, v.shape[1]))
    for i in range(seq_len):  # 第 i 个位置作为查询
        scores = np.array([q[i] @ k[j] / np.sqrt(d_k) for j in range(seq_len)])  # 与每个位置的相似度
        weights = softmax(scores)  # 变成概率分布
        output[i] = sum(weights[j] * v[j] for j in range(seq_len))  # 加权求和
    return output


def attention(q: FloatArray, k: FloatArray, v: FloatArray, causal: bool = False) -> tuple[FloatArray, FloatArray]:
    """进阶版：矩阵乘法一次算完；causal=True 时屏蔽未来位置。返回 (输出, 注意力权重)。"""
    d_k = q.shape[-1]
    scores = q @ k.T / np.sqrt(d_k)  # 形状 (T_q, T_k)
    if causal:
        seq_len = scores.shape[0]
        future = np.triu(np.ones((seq_len, seq_len), dtype=bool), k=1)  # 上三角：未来位置
        scores = np.where(future, -np.inf, scores)  # 未来位置打成 -inf
    weights = softmax(scores)
    return weights @ v, weights


def run_tests() -> None:
    """自动化断言测试：覆盖循环与矩阵写法的一致性、权重性质与因果掩码。"""
    rng = np.random.default_rng(0)  # 固定随机种子，保证每次结果一致
    seq_len, d_k, d_v = 4, 3, 2
    q = rng.normal(size=(seq_len, d_k))
    k = rng.normal(size=(seq_len, d_k))
    v = rng.normal(size=(seq_len, d_v))

    # 1. 循环版与矩阵版结果一致
    out_matrix, weights = attention(q, k, v)
    assert np.allclose(attention_loop(q, k, v), out_matrix)

    # 2. 权重每一行加起来为 1，且都非负
    assert np.allclose(weights.sum(axis=-1), 1.0)
    assert (weights >= 0).all()

    # 3. 因果掩码：第一行只能看到自己，权重 [1, 0, 0, 0]，输出等于 V[0]
    causal_out, causal_w = attention(q, k, v, causal=True)
    assert np.allclose(causal_w[0], [1.0, 0.0, 0.0, 0.0])
    assert np.allclose(causal_out[0], v[0])
    assert np.allclose(np.triu(causal_w, k=1), 0.0)  # 上三角（未来）全部为 0

    # 4. softmax 数值稳定：输入很大也不会得到 nan
    big = softmax(np.array([1000.0, 1000.0, 999.0]))
    assert np.isfinite(big).all() and np.isclose(big.sum(), 1.0)

    # 5. 边界：只有一个位置时，注意力就是 V 本身
    single_out, _ = attention(q[:1], k[:1], v[:1])
    assert np.allclose(single_out, v[:1])

    print('✅ 缩放点积注意力所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 缩放点积注意力 {'*' * 12}", sep='', end='\n\n')
    rng = np.random.default_rng(42)
    tokens = ['我', '爱', 'Python', '编程']
    x = rng.normal(size=(len(tokens), 3))
    output, weights = attention(x, x, x, causal=True)  # 自注意力：Q、K、V 都来自同一输入
    print('因果注意力权重（行=查询词，列=被关注的词）:')
    print(np.round(weights, 2))
    print('输出形状:', output.shape)
    run_tests()


if __name__ == '__main__':
    bootstrap()
