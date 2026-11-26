"""
[题目编号]: LeetCode 518. 零钱兑换 II (Coin Change II)
[难度]: Medium (完全背包求组合数；与 LC 322 求最少个数对照)
[所属专题]: 10_dynamic_programming
[前置知识]: 10_dynamic_programming/01_lc0322_coin_change、完全背包正序

一、题目描述
给你一个整数数组 `coins` 表示不同面额的硬币，另给一个整数 `amount` 表示总金额。
请你计算并返回可以凑成总金额的硬币组合数。如果任何硬币组合都无法凑出，返回 0。
假设每一种面额的硬币有无限个。顺序不同的组合视为同一种（求组合而非排列）。

示例:
- amount=5, coins=[1, 2, 5] -> 4  （5=5 / 2+2+1 / 2+1+1+1 / 1+1+1+1+1）
- amount=3, coins=[2] -> 0
- amount=10, coins=[10] -> 1

二、解法与遍历顺序要点
`dp[x]` = 凑出金额 x 的组合数；`dp[0] = 1`。
外层遍历硬币、内层正序遍历金额：`dp[x] += dp[x - coin]`。
为什么外层必须是硬币？保证「先用完一种面额再考虑下一种」，避免把 [1,2] 与 [2,1] 算成两种。

与 LC 322: 322 求最少个数用 `min`；本题求组合数用累加。

三、工程映射
- 方案计数: 支付拆单组合数、资源配额组合方案数（不计顺序）。
"""

from __future__ import annotations


def change(amount: int, coins: list[int]) -> int:
    """完全背包求组合数：外层硬币、内层正序金额。"""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] += dp[x - coin]
    return dp[amount]


def run_tests() -> None:
    assert change(5, [1, 2, 5]) == 4
    assert change(3, [2]) == 0
    assert change(10, [10]) == 1
    assert change(0, [1, 2]) == 1
    assert change(4, [1, 2, 3]) == 4
    print('✅ LeetCode 518 (零钱兑换 II / 组合数) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 518. 零钱兑换 II {'*' * 12}", sep='', end='\n\n')
    print(change(5, [1, 2, 5]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
