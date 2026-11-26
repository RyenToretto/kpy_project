"""
[主题]: 迷你 GPT 前向传播 (Token/位置 Embedding -> 因果自注意力 -> MLP -> 输出 Logits)
[来源]: rasbt/LLMs-from-scratch 第 3~4 章「实现一个类 GPT 模型」(本文件为自行重写的 NumPy 学习版)
[难度]: Hard
[前置知识]: 09_happy_llm/00_attention_basics (注意力)、09_happy_llm/02_norm_and_rope (LayerNorm 思路)、01_bigram_lm (交叉熵)

一、主题说明
GPT 的结构可以拆成几块乐高：
1. Embedding: token ID -> 向量，再加上位置向量，告诉模型“谁在第几个位置”；
2. 因果自注意力: 每个位置只能看见自己与之前的位置；
3. MLP: 对每个位置独立做非线性变换，让模型有“加工”能力；
4. 残差连接 + LayerNorm: 让深层网络可训练；
5. 输出头: 把隐藏向量投影回词表大小，得到下一个 token 的 logits。
本文件把这五块拼成一次完整前向，并用性质检验：因果性、初始损失接近 log(V)、形状正确。

二、解法对比（以「让每个位置看见上下文」为例）
1. 直观版 mean_context: 直接对前面所有位置的向量取平均作为上下文（没有可学习参数）。
   - 时间复杂度 O(T^2 * D)，无法区分不同位置的重要程度。
2. 进阶版 causal_self_attention: 用可学习的 Q、K、V 投影，让模型自己决定关注谁。
   - 时间复杂度 O(T^2 * D)，空间复杂度 O(T^2)；这是 GPT 的核心。

三、真实用途
- 大数据: 大规模预训练就是对这套前向反复做梯度更新，理解它有助于估算算力与显存。
- 数据分析: 用类 GPT 模型做序列预测（如用户行为序列、日志异常），结构完全相同。
- AI Agent / RAG: 所有对话模型的推理都是这套前向，输出 logits 后再做采样或束搜索。
- 全栈开发: 部署模型时，参数量、层数、隐藏维度直接决定显存与延迟，这是选型的依据。
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def layernorm(x: FloatArray, eps: float = 1e-5) -> FloatArray:
    """LayerNorm：沿特征维度减均值、除标准差（这里省略了可学习的缩放与偏移，便于阅读）。"""
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + eps)


def gelu(x: FloatArray) -> FloatArray:
    """GELU 激活函数（tanh 近似），比 ReLU 更平滑，GPT 系列普遍使用。"""
    return 0.5 * x * (1.0 + np.tanh(np.sqrt(2.0 / np.pi) * (x + 0.044715 * x**3)))


def softmax(scores: FloatArray) -> FloatArray:
    """沿最后一维做数值稳定的 softmax。"""
    shifted = scores - np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(shifted)
    return exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)


def mean_context(x: FloatArray) -> FloatArray:
    """直观版：每个位置的上下文 = 前面所有位置向量的平均（没有可学习参数）。"""
    out = np.zeros_like(x)
    for t in range(x.shape[0]):
        out[t] = np.mean(x[: t + 1], axis=0)
    return out


@dataclass
class GPTParams:
    """迷你 GPT 的全部参数。"""

    tok_emb: FloatArray  # (V, D) 词向量表
    pos_emb: FloatArray  # (block_size, D) 位置向量表
    wq: FloatArray  # (D, D)
    wk: FloatArray  # (D, D)
    wv: FloatArray  # (D, D)
    wo: FloatArray  # (D, D)
    w1: FloatArray  # (D, 4D) MLP 第一层
    w2: FloatArray  # (4D, D) MLP 第二层


def init_params(vocab_size: int, dim: int, block_size: int, seed: int = 0) -> GPTParams:
    """用很小的随机数初始化参数，让初始输出接近均匀分布，便于检查初始损失。"""
    rng = np.random.default_rng(seed)

    def weight(*shape: int) -> FloatArray:
        return rng.normal(scale=0.02, size=shape)

    return GPTParams(
        tok_emb=weight(vocab_size, dim),
        pos_emb=weight(block_size, dim),
        wq=weight(dim, dim),
        wk=weight(dim, dim),
        wv=weight(dim, dim),
        wo=weight(dim, dim),
        w1=weight(dim, 4 * dim),
        w2=weight(4 * dim, dim),
    )


def causal_self_attention(x: FloatArray, p: GPTParams) -> FloatArray:
    """单头因果自注意力：每个位置只能看见自己及之前的位置。"""
    q, k, v = x @ p.wq, x @ p.wk, x @ p.wv
    scores = q @ k.T / np.sqrt(x.shape[-1])
    seq_len = x.shape[0]
    future = np.triu(np.ones((seq_len, seq_len), dtype=bool), k=1)
    scores = np.where(future, -np.inf, scores)  # 屏蔽未来位置
    return softmax(scores) @ v @ p.wo


def forward(tokens: NDArray[np.int64], p: GPTParams) -> FloatArray:
    """完整前向：返回形状 (T, V) 的 logits，第 t 行是“第 t 个位置之后的下一个 token”的打分。"""
    seq_len = tokens.shape[0]
    x = p.tok_emb[tokens] + p.pos_emb[:seq_len]  # 词向量 + 位置向量
    # 注意力子层：Pre-LN + 残差
    x = x + causal_self_attention(layernorm(x), p)
    # MLP 子层：Pre-LN + 残差
    x = x + gelu(layernorm(x) @ p.w1) @ p.w2
    # 输出头：权重与词向量表共享（weight tying），节省参数
    return layernorm(x) @ p.tok_emb.T


def cross_entropy(logits: FloatArray, targets: NDArray[np.int64]) -> float:
    """平均交叉熵：-mean(log P(正确 token))。"""
    probs = softmax(logits)
    n = logits.shape[0]
    return float(-np.mean(np.log(probs[np.arange(n), targets] + 1e-12)))


def run_tests() -> None:
    """自动化断言测试：覆盖形状、因果性、初始损失与边界用例。"""
    vocab, dim, block = 20, 8, 16
    params = init_params(vocab, dim, block, seed=0)
    rng = np.random.default_rng(1)
    tokens = rng.integers(0, vocab, size=6)

    # 1. 输出形状：(序列长度, 词表大小)
    logits = forward(tokens, params)
    assert logits.shape == (6, vocab)

    # 2. 因果性：修改最后一个 token，前面位置的 logits 不变
    changed = tokens.copy()
    changed[-1] = (changed[-1] + 1) % vocab
    logits_changed = forward(changed, params)
    assert np.allclose(logits[:-1], logits_changed[:-1])
    assert not np.allclose(logits[-1], logits_changed[-1])

    # 3. 初始损失接近 log(V)：随机初始化时模型近似均匀猜测
    targets = rng.integers(0, vocab, size=6)
    loss = cross_entropy(logits, targets)
    assert abs(loss - np.log(vocab)) < 0.3

    # 4. 注意力子层不改变序列长度与维度
    x = params.tok_emb[tokens] + params.pos_emb[:6]
    assert causal_self_attention(layernorm(x), params).shape == x.shape

    # 5. 边界：长度为 1 的序列也能前向，只输出 1 行
    assert forward(tokens[:1], params).shape == (1, vocab)

    # 6. 直观版上下文平均：第一个位置只看见自己
    x_demo = rng.normal(size=(4, 3))
    assert np.allclose(mean_context(x_demo)[0], x_demo[0])

    print('✅ 迷你 GPT 前向传播所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 迷你 GPT 前向传播 {'*' * 12}", sep='', end='\n\n')
    vocab, dim, block = 20, 8, 16
    params = init_params(vocab, dim, block, seed=0)
    tokens = np.array([3, 7, 1, 5])
    logits = forward(tokens, params)
    print('输入 token:', tokens.tolist())
    print('输出 logits 形状:', logits.shape)
    print('最后位置 Top-3 候选 token:', np.argsort(logits[-1])[::-1][:3].tolist())
    run_tests()


if __name__ == '__main__':
    bootstrap()
