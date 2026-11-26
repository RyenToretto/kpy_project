"""
[主题]: LoRA 低秩适配微调 (Low-Rank Adaptation) 与权重合并
[来源]: datawhalechina/happy-llm 第 5 章「大模型微调」(本文件为自行重写的 NumPy 学习版)
[难度]: Hard
[前置知识]: 09_happy_llm/02_norm_and_rope (线性层)、矩阵乘法、梯度下降的直觉

一、主题说明
全量微调要更新大模型的每一个参数，显存与存储成本极高。LoRA 的思路是：
- 冻结原始权重 W（d_in × d_out）；
- 只训练两个小矩阵 A（d_in × r）和 B（r × d_out），r 远小于 d；
- 前向: y = x·W + (alpha / r)·x·A·B；
- B 初始化为 0，所以训练开始时 LoRA 分支输出为 0，模型行为与原模型一致；
- 训练完成后可以把 W + (alpha/r)·A·B 合并成一个矩阵，推理时没有额外延迟。

二、解法对比（以「让一个线性层适应新任务」为例）
1. 直观版 full_finetune_params: 直接更新整个 W，参数量 d_in × d_out。
   - 参数量 O(d^2)，每个新任务都要保存一整份模型。
2. 进阶版 LoRALinear: 只训练 A、B，参数量 r × (d_in + d_out)。
   - 参数量 O(r·d)，当 r = 8、d = 4096 时，约为全量的 0.4%。

三、真实用途
- 大数据: 同一个基座模型可以为不同业务线训练多个小适配器，共享底座、节省存储。
- 数据分析: 用行业语料微调模型（如财报、医疗报告）时，LoRA 让普通显卡也能完成。
- AI Agent / RAG: 让 Agent 学会特定工具的调用格式，只需训练很少的参数。
- 全栈开发: 部署时按客户切换 LoRA 适配器，是 SaaS 化大模型服务的常见架构。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def full_finetune_params(d_in: int, d_out: int) -> int:
    """直观版：全量微调需要训练的参数个数 = d_in × d_out。"""
    return d_in * d_out


@dataclass
class LoRALinear:
    """带 LoRA 分支的线性层：W 冻结，只训练 A 与 B。"""

    weight: FloatArray  # 冻结的原始权重，形状 (d_in, d_out)
    rank: int
    alpha: float = 16.0
    a: FloatArray = field(init=False)  # 形状 (d_in, r)
    b: FloatArray = field(init=False)  # 形状 (r, d_out)，初始为 0

    def __post_init__(self) -> None:
        rng = np.random.default_rng(0)
        d_in = self.weight.shape[0]
        d_out = self.weight.shape[1]
        self.a = rng.normal(scale=0.01, size=(d_in, self.rank))  # A 用小随机数初始化
        self.b = np.zeros((self.rank, d_out))  # B 全零：起点时 LoRA 分支输出为 0

    @property
    def scale(self) -> float:
        """缩放系数 alpha / r，让不同 rank 下的学习率更容易对齐。"""
        return self.alpha / self.rank

    def forward(self, x: FloatArray) -> FloatArray:
        """前向：原始输出 + 低秩修正量。"""
        return x @ self.weight + self.scale * (x @ self.a) @ self.b

    def merged_weight(self) -> FloatArray:
        """合并：把 LoRA 修正直接加回 W，推理时只需一次矩阵乘法。"""
        return self.weight + self.scale * (self.a @ self.b)

    def trainable_params(self) -> int:
        """可训练参数个数 = r × (d_in + d_out)。"""
        return self.a.size + self.b.size

    def train_step(self, x: FloatArray, target: FloatArray, lr: float = 0.01) -> float:
        # 注意：学习率过大（如 0.1）会让损失发散成 nan，这是训练中最常见的问题之一
        """做一步梯度下降，只更新 A 和 B，返回 MSE 损失。损失 L = mean((y_pred - y)^2) / 2。"""
        pred = self.forward(x)
        error = pred - target  # 形状 (N, d_out)
        n = x.shape[0]
        loss = float(np.sum(error * error) / (2 * n))
        grad_out = error / n  # dL/dy
        grad_b = self.scale * (x @ self.a).T @ grad_out  # dL/dB
        grad_a = self.scale * x.T @ (grad_out @ self.b.T)  # dL/dA（W 不参与更新）
        self.b -= lr * grad_b
        self.a -= lr * grad_a
        return loss


def run_tests() -> None:
    """自动化断言测试：覆盖零初始化、合并等价、参数量与训练下降。"""
    rng = np.random.default_rng(5)
    d_in, d_out, rank = 16, 8, 2
    weight = rng.normal(size=(d_in, d_out))
    layer = LoRALinear(weight, rank=rank, alpha=16.0)
    x = rng.normal(size=(32, d_in))

    # 1. 初始时 B 为 0，LoRA 输出与原模型完全一致
    assert np.allclose(layer.forward(x), x @ weight)

    # 2. 参数量远少于全量微调
    assert layer.trainable_params() == rank * (d_in + d_out)
    assert layer.trainable_params() < full_finetune_params(d_in, d_out)

    # 3. 训练几步后，合并权重的结果与分支前向完全一致
    target = rng.normal(size=(32, d_out))
    first_loss = layer.train_step(x, target)
    for _ in range(20):
        last_loss = layer.train_step(x, target)
    assert last_loss < first_loss  # 损失确实在下降
    assert np.allclose(x @ layer.merged_weight(), layer.forward(x))

    # 4. 冻结的 W 没有被修改
    assert np.allclose(layer.weight, weight)

    # 5. 边界：rank 不同时缩放系数不同，alpha/r 随 rank 变化
    assert LoRALinear(weight, rank=4, alpha=16.0).scale == 4.0
    assert LoRALinear(weight, rank=8, alpha=16.0).scale == 2.0

    print('✅ LoRA 低秩适配所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LoRA 低秩适配 {'*' * 12}", sep='', end='\n\n')
    d_in, d_out, rank = 4096, 4096, 8
    print(f'全量微调参数量: {full_finetune_params(d_in, d_out):,}')
    layer = LoRALinear(np.zeros((d_in, d_out)), rank=rank)
    ratio = layer.trainable_params() / full_finetune_params(d_in, d_out)
    print(f'LoRA(r={rank}) 参数量: {layer.trainable_params():,}，约为全量的 {ratio:.2%}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
