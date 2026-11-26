"""
[主题]: 最简语言模型 Bigram：用手写梯度训练「下一个字符预测」并采样生成
[来源]: rasbt/LLMs-from-scratch 第 3~4 章「从零训练语言模型」思路 (本文件为自行重写的 NumPy 学习版)
[难度]: Medium
[前置知识]: 10_llms_from_scratch/00_tokenizer (分词)、09_happy_llm/00_attention_basics (softmax)、梯度下降

一、主题说明
语言模型的核心任务只有一件事：给定前文，预测下一个 token 的概率分布。
Bigram 只看前一个 token，参数就是一张 V × V 的表 W：W[i, j] 表示“i 之后出现 j”的得分。
训练目标是交叉熵：让正确下一个 token 的概率尽量大，等价于最小化 -log P(正确答案)。
- 前向: logits = W[前一个 token]，probs = softmax(logits)；
- 梯度: dlogits = probs - onehot(正确答案)，再累加到 W 对应的行；
- 训练后用 probs 逐个采样，就能“生成”文本。
这是 GPT 训练的最小版本：GPT 只是把 W[前一个 token] 换成了一个更复杂的 Transformer。

二、解法对比（以「统计下一个字符的概率」为例）
1. 直观版 count_bigram: 直接统计每对字符出现次数，归一化得到概率（没有训练过程）。
   - 时间复杂度 O(N)，空间复杂度 O(V^2)。
2. 进阶版 BigramLM.train: 用梯度下降学习 W，能自然扩展到更复杂的模型。
   - 每步时间复杂度 O(N * V)，空间复杂度 O(V^2)。两者在数据充足时结果应接近。

三、真实用途
- 大数据: 语言模型是海量文本处理的基础，困惑度（perplexity）可用来评估数据质量。
- 数据分析: 字符级模型可用于异常文本检测（低概率序列往往是异常输入）。
- AI Agent / RAG: 生成质量评估、输入合法性检测都会用到语言模型概率。
- 全栈开发: 输入法联想、搜索框自动补全，本质都是这种“给定前文预测下文”。
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def softmax(logits: FloatArray) -> FloatArray:
    """沿最后一维做数值稳定的 softmax。"""
    shifted = logits - np.max(logits, axis=-1, keepdims=True)
    exp_logits = np.exp(shifted)
    return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


def count_bigram(tokens: list[int], vocab_size: int) -> FloatArray:
    """直观版：直接数每对出现的次数，再按行归一化得到概率表。"""
    counts = np.zeros((vocab_size, vocab_size))
    for prev, nxt in zip(tokens, tokens[1:]):
        counts[prev, nxt] += 1
    row_sums = counts.sum(axis=1, keepdims=True)
    return np.divide(counts, row_sums, out=np.zeros_like(counts), where=row_sums > 0)


class BigramLM:
    """Bigram 模型：参数 W 形状 (V, V)，W[i] 是“前一个词为 i 时”下一个词的打分。"""

    def __init__(self, vocab_size: int, seed: int = 0) -> None:
        rng = np.random.default_rng(seed)
        self.vocab_size = vocab_size
        self.weight = rng.normal(scale=0.01, size=(vocab_size, vocab_size))  # 小随机数初始化

    def loss_and_grad(self, inputs: NDArray[np.int64], targets: NDArray[np.int64]) -> tuple[float, FloatArray]:
        """计算平均交叉熵损失与对 W 的梯度（手写反向传播，不依赖自动求导）。"""
        n = inputs.shape[0]
        logits = self.weight[inputs]  # 形状 (N, V)
        probs = softmax(logits)
        loss = float(-np.mean(np.log(probs[np.arange(n), targets] + 1e-12)))  # 1e-12 防止 log(0)
        dlogits = probs.copy()
        dlogits[np.arange(n), targets] -= 1.0  # softmax + 交叉熵的梯度 = probs - onehot
        dlogits /= n  # 对 batch 求平均
        grad = np.zeros_like(self.weight)
        np.add.at(grad, inputs, dlogits)  # 同一个 input 可能出现多次，必须用 add.at 累加
        return loss, grad

    def train(self, inputs: NDArray[np.int64], targets: NDArray[np.int64], steps: int, lr: float = 1.0) -> list[float]:
        """梯度下降训练，返回每一步的损失，便于观察是否收敛。"""
        history: list[float] = []
        for _ in range(steps):
            loss, grad = self.loss_and_grad(inputs, targets)
            self.weight -= lr * grad
            history.append(loss)
        return history

    def next_probs(self, token: int) -> FloatArray:
        """给定前一个 token，返回下一个 token 的概率分布。"""
        return softmax(self.weight[token])

    def generate(self, start: int, length: int, seed: int = 0) -> list[int]:
        """按概率逐个采样生成序列；seed 固定时结果可复现。"""
        rng = np.random.default_rng(seed)
        out = [start]
        for _ in range(length):
            probs = self.next_probs(out[-1])
            out.append(int(rng.choice(self.vocab_size, p=probs)))
        return out


def make_pairs(tokens: list[int]) -> tuple[NDArray[np.int64], NDArray[np.int64]]:
    """把 token 序列切成 (前一个, 下一个) 训练对。"""
    inputs = np.array(tokens[:-1], dtype=np.int64)
    targets = np.array(tokens[1:], dtype=np.int64)
    return inputs, targets


def run_tests() -> None:
    """自动化断言测试：覆盖损失下降、学到的概率、采样可复现与边界用例。"""
    # 语料：字符 a=0, b=1, c=2，规律是 a -> b -> c -> a 循环
    tokens = [0, 1, 2] * 10
    inputs, targets = make_pairs(tokens)

    # 1. 训练后损失明显下降
    model = BigramLM(vocab_size=3, seed=0)
    history = model.train(inputs, targets, steps=200, lr=5.0)
    assert history[-1] < history[0] * 0.5

    # 2. 学到的规律：看到 a(0) 之后 b(1) 的概率应接近 1
    assert model.next_probs(0)[1] > 0.9
    assert model.next_probs(1)[2] > 0.9

    # 3. 与直观计数版得到的概率方向一致
    counted = count_bigram(tokens, vocab_size=3)
    assert np.argmax(counted[0]) == np.argmax(model.next_probs(0)) == 1

    # 4. 概率每行和为 1
    assert np.allclose(model.next_probs(2).sum(), 1.0)

    # 5. 采样可复现：同一个 seed 生成的序列完全相同，并且遵循 a -> b -> c 的规律
    sample_a = model.generate(start=0, length=6, seed=42)
    sample_b = model.generate(start=0, length=6, seed=42)
    assert sample_a == sample_b
    assert sample_a[:4] == [0, 1, 2, 0]

    # 6. 边界：梯度的形状与权重一致
    _, grad = model.loss_and_grad(inputs, targets)
    assert grad.shape == model.weight.shape

    print('✅ Bigram 语言模型所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} Bigram 语言模型训练 {'*' * 12}", sep='', end='\n\n')
    tokens = [0, 1, 2] * 10
    inputs, targets = make_pairs(tokens)
    model = BigramLM(vocab_size=3, seed=0)
    history = model.train(inputs, targets, steps=200, lr=5.0)
    print(f'训练损失: 第 1 步 {history[0]:.4f} -> 第 200 步 {history[-1]:.4f}')
    print('看到 a(0) 后，下一个字符的概率:', np.round(model.next_probs(0), 3))
    print('采样生成:', model.generate(start=0, length=8, seed=1))
    run_tests()


if __name__ == '__main__':
    bootstrap()
