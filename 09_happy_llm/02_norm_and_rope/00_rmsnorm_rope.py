"""
[主题]: RMSNorm 归一化与 RoPE 旋转位置编码 (Rotary Position Embedding)
[来源]: datawhalechina/happy-llm 第 2 章「位置编码与归一化」(本文件为自行重写的 NumPy 学习版)
[难度]: Medium
[前置知识]: 09_happy_llm/00_attention_basics (注意力)、三角函数、向量点积

一、主题说明
- 归一化: 深层网络里数值会越传越大或越小。RMSNorm 只除以均方根（不减均值），比 LayerNorm 更简单，LLaMA 等主流模型都在用。
- 位置编码: 注意力本身不知道词的先后顺序，必须额外告诉模型位置。
- RoPE: 不是把位置向量加到词向量上，而是把 q、k 按位置旋转一个角度。
  关键性质：两个位置 m、n 的 q、k 点积只依赖相对距离 m-n，与绝对位置无关，所以长上下文外推更自然。

二、解法对比（以「给每个位置加上位置信息」为例）
1. 直观版 add_sinusoidal_pos: 把固定的正余弦位置向量直接加到输入上（原始 Transformer 的做法）。
   - 时间复杂度 O(T * D)，位置信息与内容混在一起。
2. 进阶版 apply_rope: 对每一对维度做二维旋转，角度 = 位置 × 频率。
   - 时间复杂度 O(T * D)，且不改变向量长度，相对位置信息直接体现在点积中。

三、真实用途
- 大数据: 长序列建模（日志、基因、时间序列）需要稳定的位置表示，RoPE 能更好地外推到更长的序列。
- 数据分析: 模型对表格或时间序列的顺序敏感，位置编码决定了它是否“理解先后”。
- AI Agent / RAG: 长上下文的检索拼接依赖位置外推能力，RoPE 是 LLaMA、Qwen 等模型的标配。
- 全栈开发: 部署长上下文模型时，要知道 RoPE 的基频（base）设置会影响能支持的最大长度。
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def rmsnorm(x: FloatArray, weight: FloatArray, eps: float = 1e-6) -> FloatArray:
    """RMSNorm: x / sqrt(mean(x^2) + eps) * weight。沿最后一维归一化，eps 防止除零。"""
    rms = np.sqrt(np.mean(x * x, axis=-1, keepdims=True) + eps)
    return x / rms * weight


def layernorm_naive(x: FloatArray, eps: float = 1e-6) -> FloatArray:
    """直观对照版：LayerNorm 同时减去均值再除以标准差（不带可学习参数，便于对比）。"""
    mean = np.mean(x, axis=-1, keepdims=True)
    std = np.sqrt(np.var(x, axis=-1, keepdims=True) + eps)
    return (x - mean) / std


def sinusoidal_pos(seq_len: int, dim: int) -> FloatArray:
    """直观版位置编码：原始 Transformer 的正余弦位置向量，直接加到词向量上。"""
    positions = np.arange(seq_len)[:, None]
    freqs = 1.0 / (10000 ** (np.arange(0, dim, 2) / dim))
    pe = np.zeros((seq_len, dim))
    pe[:, 0::2] = np.sin(positions * freqs)
    pe[:, 1::2] = np.cos(positions * freqs)
    return pe


def rope_angles(positions: FloatArray, dim: int, base: float = 10000.0) -> FloatArray:
    """计算每个位置、每对维度的旋转角：角度 = 位置 × 频率，频率随维度递减。"""
    freqs = 1.0 / (base ** (np.arange(0, dim, 2) / dim))  # 形状 (dim/2,)
    return np.outer(positions, freqs)  # 形状 (T, dim/2)


def apply_rope(x: FloatArray, positions: FloatArray, base: float = 10000.0) -> FloatArray:
    """对 x（形状 (T, dim)）做 RoPE：每相邻两维 (x1, x2) 旋转 angle。
    旋转公式: [x1', x2'] = [x1*cos - x2*sin, x1*sin + x2*cos]。"""
    dim = x.shape[-1]
    angles = rope_angles(positions, dim, base)
    cos, sin = np.cos(angles), np.sin(angles)
    x1, x2 = x[:, 0::2], x[:, 1::2]  # 把维度两两配对
    out = np.empty_like(x)
    out[:, 0::2] = x1 * cos - x2 * sin
    out[:, 1::2] = x1 * sin + x2 * cos
    return out


def run_tests() -> None:
    """自动化断言测试：覆盖归一化尺度、旋转保范数、相对位置性质与边界用例。"""
    rng = np.random.default_rng(3)

    # 1. RMSNorm：权重全为 1 时，输出的均方根接近 1
    x = rng.normal(size=(4, 8)) * 10.0
    normed = rmsnorm(x, np.ones(8))
    rms = np.sqrt(np.mean(normed * normed, axis=-1))
    assert np.allclose(rms, 1.0, atol=1e-4)

    # 2. 对照：RMSNorm 不减均值，LayerNorm 会减均值，两者结果不同
    shifted = x + 5.0
    assert not np.allclose(rmsnorm(shifted, np.ones(8)), layernorm_naive(shifted))

    # 3. RoPE 是旋转，不改变向量长度
    q = rng.normal(size=(6, 8))
    rotated = apply_rope(q, np.arange(6, dtype=float))
    assert np.allclose(np.linalg.norm(rotated, axis=-1), np.linalg.norm(q, axis=-1))

    # 4. 核心性质：位置 (m, n) 的点积只依赖 m - n，整体平移不改变结果
    k = rng.normal(size=(1, 8))
    q1 = rng.normal(size=(1, 8))
    m, n, shift = 5.0, 2.0, 10.0
    dot_a = apply_rope(q1, np.array([m])) @ apply_rope(k, np.array([n])).T
    dot_b = apply_rope(q1, np.array([m + shift])) @ apply_rope(k, np.array([n + shift])).T
    assert np.allclose(dot_a, dot_b)

    # 5. 位置 0 不旋转：RoPE 在第 0 个位置等于原向量
    assert np.allclose(apply_rope(q[:1], np.array([0.0])), q[:1])

    # 6. 直观版位置编码的形状正确（加法式，不保证范数不变）
    assert sinusoidal_pos(6, 8).shape == (6, 8)

    print('✅ RMSNorm 与 RoPE 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} RMSNorm 与 RoPE {'*' * 12}", sep='', end='\n\n')
    rng = np.random.default_rng(0)
    x = rng.normal(size=(3, 4))
    print('RMSNorm 输出:\n', np.round(rmsnorm(x, np.ones(4)), 3))
    q = np.ones((3, 4))
    print('RoPE 旋转后（位置 0/1/2）:\n', np.round(apply_rope(q, np.arange(3, dtype=float)), 3))
    run_tests()


if __name__ == '__main__':
    bootstrap()
