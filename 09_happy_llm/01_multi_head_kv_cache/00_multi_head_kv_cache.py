"""
[主题]: 多头注意力 (Multi-Head Attention) 与 KV Cache 增量解码
[来源]: datawhalechina/happy-llm 第 2~3 章「多头注意力与推理加速」(本文件为自行重写的 NumPy 学习版)
[难度]: Medium
[前置知识]: 09_happy_llm/00_attention_basics (缩放点积注意力、因果掩码)

一、主题说明
- 多头: 把隐藏维度 D 切成 H 份，每个头在不同的“子空间”里各自关注不同关系（指代、语法、语义……），最后拼回去。
- 自回归生成时，模型一个词一个词地输出。如果每一步都把整段历史重新算一遍 K、V，会重复大量计算。
- KV Cache: 把已经算过的历史 K、V 存起来，每生成一个新词，只需计算这一个词的 q、k、v，再和缓存拼接。
  结果与整段重算完全一致，但每步计算量从 O(T^2) 降到约 O(T)。代价是显存随上下文长度线性增长。

二、解法对比（以「生成 T 个词」为例）
1. 直观版 decode_recompute: 每一步都把整段序列重新做一次完整注意力。
   - 总时间复杂度 O(T^3)，空间复杂度 O(T^2)（每步的注意力矩阵）。
2. 进阶版 KVCacheDecoder: 每步只算新词的 q、k、v，历史 K、V 从缓存读取。
   - 总时间复杂度 O(T^2)，空间复杂度 O(T * D)（缓存随长度增长）。

三、真实用途
- 大数据: 批量离线推理时，KV Cache 决定了同样显存下能同时处理多少条请求。
- 数据分析: 用大模型做长文档摘要或报表解读时，上下文越长，缓存占用越大，需要控制成本。
- AI Agent / RAG: 多轮工具调用会不断拉长上下文，KV Cache 的管理（截断、压缩）是性能关键。
- 全栈开发: vLLM、TGI 等推理框架的核心优化之一就是 PagedAttention 式的 KV Cache 管理。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def softmax(scores: FloatArray) -> FloatArray:
    """数值稳定的 softmax，沿最后一个轴归一化。"""
    shifted = scores - np.max(scores, axis=-1, keepdims=True)
    exp_scores = np.exp(shifted)
    return exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)


def to_heads(x: FloatArray, n_heads: int) -> FloatArray:
    """把 (T, D) 拆成 (H, T, D/H)：每个头拿到 D 的一个子空间。"""
    seq_len, dim = x.shape
    head_dim = dim // n_heads
    return x.reshape(seq_len, n_heads, head_dim).transpose(1, 0, 2)


def from_heads(x: FloatArray) -> FloatArray:
    """把 (H, T, D/H) 合并回 (T, D)，与 to_heads 互为逆操作。"""
    n_heads, seq_len, head_dim = x.shape
    return x.transpose(1, 0, 2).reshape(seq_len, n_heads * head_dim)


def attend(q: FloatArray, k: FloatArray, v: FloatArray, causal: bool) -> FloatArray:
    """多头注意力核心：q 形状 (H, T_q, d)，k/v 形状 (H, T_k, d)。
    因果掩码对齐到右侧：查询第 i 个位置（在整段序列中是 offset+i）只能看 <= offset+i 的键。"""
    head_dim = q.shape[-1]
    scores = q @ k.transpose(0, 2, 1) / np.sqrt(head_dim)  # 形状 (H, T_q, T_k)
    if causal:
        t_q, t_k = scores.shape[1], scores.shape[2]
        offset = t_k - t_q  # 已缓存的历史长度
        rows = np.arange(t_q)[:, None] + offset
        cols = np.arange(t_k)[None, :]
        scores = np.where(cols > rows, -np.inf, scores)  # 屏蔽未来位置
    return softmax(scores) @ v


def decode_recompute(x: FloatArray, wq: FloatArray, wk: FloatArray, wv: FloatArray, wo: FloatArray, n_heads: int) -> FloatArray:
    """直观版：每一步都把整段序列重新做一次完整的因果多头注意力。"""
    outputs: list[FloatArray] = []
    for t in range(1, x.shape[0] + 1):  # 依次“生成”第 1、2、…、T 个位置
        prefix = x[:t]  # 每一步都重新使用全部历史
        q = to_heads(prefix @ wq, n_heads)
        k = to_heads(prefix @ wk, n_heads)
        v = to_heads(prefix @ wv, n_heads)
        full = from_heads(attend(q, k, v, causal=True)) @ wo
        outputs.append(full[-1])  # 只取最后一个位置作为本步的输出
    return np.stack(outputs)


@dataclass
class KVCacheDecoder:
    """带 KV Cache 的增量解码器：缓存的 k、v 形状为 (H, t, d)，随生成步数增长。"""

    wq: FloatArray
    wk: FloatArray
    wv: FloatArray
    wo: FloatArray
    n_heads: int
    cache_k: FloatArray | None = field(default=None, init=False)
    cache_v: FloatArray | None = field(default=None, init=False)

    def step(self, x_t: FloatArray) -> FloatArray:
        """处理一个新词：只计算它自己的 q、k、v，再和缓存拼接。"""
        row = x_t[None, :]  # 形状 (1, D)，便于复用 to_heads
        q = to_heads(row @ self.wq, self.n_heads)
        k_new = to_heads(row @ self.wk, self.n_heads)
        v_new = to_heads(row @ self.wv, self.n_heads)
        if self.cache_k is None:
            self.cache_k, self.cache_v = k_new, v_new
        else:
            self.cache_k = np.concatenate([self.cache_k, k_new], axis=1)  # 沿时间轴追加
            self.cache_v = np.concatenate([self.cache_v, v_new], axis=1)
        # 新词只能看见缓存里的全部历史（包括它自己），因此不需要再加因果掩码
        out = attend(q, self.cache_k, self.cache_v, causal=False)
        return (from_heads(out) @ self.wo)[0]

    def cache_size(self) -> int:
        """当前缓存的时间步数，用来观察显存增长。"""
        return 0 if self.cache_k is None else self.cache_k.shape[1]


def run_tests() -> None:
    """自动化断言测试：验证 KV Cache 与整段重算结果一致，并检查形状与边界。"""
    rng = np.random.default_rng(7)
    seq_len, dim, n_heads = 5, 8, 2
    x = rng.normal(size=(seq_len, dim))
    wq, wk, wv, wo = (rng.normal(size=(dim, dim)) * 0.1 for _ in range(4))

    # 1. 头的拆分与合并互为逆操作
    assert np.allclose(from_heads(to_heads(x, n_heads)), x)
    assert to_heads(x, n_heads).shape == (n_heads, seq_len, dim // n_heads)

    # 2. 核心性质：KV Cache 逐步解码 == 整段重算
    recompute = decode_recompute(x, wq, wk, wv, wo, n_heads)
    decoder = KVCacheDecoder(wq, wk, wv, wo, n_heads)
    incremental = np.stack([decoder.step(x[t]) for t in range(seq_len)])
    assert np.allclose(incremental, recompute)

    # 3. 缓存随生成步数线性增长
    assert decoder.cache_size() == seq_len

    # 4. 因果性：修改未来的词，不应影响前面位置的输出
    x_changed = x.copy()
    x_changed[-1] += 100.0
    before = decode_recompute(x, wq, wk, wv, wo, n_heads)
    after = decode_recompute(x_changed, wq, wk, wv, wo, n_heads)
    assert np.allclose(before[:-1], after[:-1])
    assert not np.allclose(before[-1], after[-1])

    # 5. 边界：只有一个词时，缓存中只有 1 个时间步
    single = KVCacheDecoder(wq, wk, wv, wo, n_heads)
    single.step(x[0])
    assert single.cache_size() == 1

    print('✅ 多头注意力与 KV Cache 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 多头注意力与 KV Cache {'*' * 12}", sep='', end='\n\n')
    rng = np.random.default_rng(1)
    dim, n_heads = 8, 2
    wq, wk, wv, wo = (rng.normal(size=(dim, dim)) * 0.1 for _ in range(4))
    decoder = KVCacheDecoder(wq, wk, wv, wo, n_heads)
    for step_index in range(1, 4):
        token_vector = rng.normal(size=dim)
        decoder.step(token_vector)
        print(f'生成第 {step_index} 个词后，KV 缓存长度 = {decoder.cache_size()}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
