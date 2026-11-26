"""
[题目编号]: LeetCode 322. 零钱兑换 (Coin Change)
[难度]: Medium (经典背包 DP 入门题，必刷！)
[所属专题]: 10_dynamic_programming
[前置知识]: LeetCode 70 爬楼梯、一维 DP 初始化技巧

一、题目描述
给你一个整数数组 `coins`（不同面额的硬币，每种硬币数量无限）和一个总金额 `amount`。
计算并返回可以凑成总金额所需的**最少硬币个数**；如果凑不出来，返回 `-1`。

示例:
- 输入: coins = [1, 2, 5], amount = 11 -> 输出: 3 (11 = 5 + 5 + 1)
- 输入: coins = [2], amount = 3 -> 输出: -1
- 边界: amount = 0 -> 0；注意不能用“每次拿最大面额”的贪心法！反例: coins = [1, 3, 4], amount = 6 (贪心拿 4+1+1=3枚，实际最优是 3+3=2枚！)

二、解法与复杂度
- 思路（自底向上一维 DP - 完全背包求最小枚数）:
  - 状态定义: `dp[x]` 表示凑出金额 `x` 所需的最少硬币数。
  - 初始化: `dp[0] = 0`，其余位置初始化为一个绝对不可能达到的大数 `amount + 1`（代表“暂时无解”）。
  - 状态转移: 对于目标金额 `x`（从 1 到 `amount`），枚举每种硬币 `coin`：
    只要 `x >= coin`，就可以尝试先拿一枚 `coin`，剩下的金额 `x - coin` 直接查表 `dp[x - coin]`：
    `dp[x] = min(dp[x], dp[x - coin] + 1)`
- 时间复杂度: O(amount * len(coins))
- 空间复杂度: O(amount)

三、工程与 AI/大数据实战映射
- 资源最优化与 Token 预算分配: 在计算任务拆包、API 计费套餐组合最省方案、模型推理 batch 凑批填充中，核心都是这种离散优化背包 DP。
"""

from __future__ import annotations


def coin_change(coins: list[int], amount: int) -> int:
    """自底向上一维 DP：求凑出 amount 的最少硬币数。"""
    if amount == 0:
        return 0

    unreachable = amount + 1  # 全用 1 元硬币最多也只需要 amount 枚，所以 amount+1 足够当“无穷大”
    dp = [unreachable] * (amount + 1)
    dp[0] = 0

    for x in range(1, amount + 1):
        for coin in coins:
            if x >= coin:
                dp[x] = min(dp[x], dp[x - coin] + 1)

    return -1 if dp[amount] == unreachable else dp[amount]


def run_tests() -> None:
    """自动化断言测试，特别包含贪心反例 [1, 3, 4], amount=6。"""
    cases = [
        ([1, 2, 5], 11, 3),
        ([2], 3, -1),
        ([1], 0, 0),
        ([1, 3, 4], 6, 2),  # 贪心反例！3 + 3 = 2 枚，而非 4 + 1 + 1 = 3 枚
        ([186, 419, 83, 408], 6249, 20),
    ]
    for coins, amount, expected in cases:
        actual = coin_change(coins, amount)
        assert actual == expected, f'失败: coins={coins}, amount={amount}, 实际={actual}'
    print('✅ LeetCode 322 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 322. 零钱兑换 {'*' * 12}", sep='', end='\n\n')
    print(f'coins=[1, 3, 4], amount=6 最少枚数: {coin_change([1, 3, 4], 6)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
