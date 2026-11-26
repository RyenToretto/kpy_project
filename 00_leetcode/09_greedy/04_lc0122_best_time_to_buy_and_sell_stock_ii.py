"""
[题目编号]: LeetCode 122. 买卖股票的最佳时机 II (Best Time to Buy and Sell Stock II)
[难度]: Medium (可多次交易的贪心累加)
[所属专题]: 09_greedy
[前置知识]: 03_sliding_window/00_lc0121_best_time_to_buy_and_sell_stock

一、题目描述
给你一个整数数组 `prices`，其中 `prices[i]` 表示某支股票第 i 天的价格。
你可以无限次地完成交易（多次买卖同一支股票），但每次最多只能持有一股。求能获得的最大利润。

示例:
- [7, 1, 5, 3, 6, 4] -> 7 (1买5卖赚4；3买6卖赚3)
- [1, 2, 3, 4, 5] -> 4
- [7, 6, 4, 3, 1] -> 0

二、解法
贪心: 所有「上涨段」的差值全部累加：`profit += max(0, prices[i] - prices[i-1])`。
等价于抓住每一段局部上升。时间 O(n)，空间 O(1)。

与 LC 121 区别: 121 只能买卖一次；本题可多次。

三、工程映射
- 多次波段收益累加: 量化里把可重复进出的正向波段利润加总；批处理任务「有涨就做」的累计收益估算。
"""

from __future__ import annotations


def max_profit(prices: list[int]) -> int:
    """把每一段上涨差值累加。"""
    profit = 0
    for i in range(1, len(prices)):
        delta = prices[i] - prices[i - 1]
        if delta > 0:
            profit += delta
    return profit


def run_tests() -> None:
    assert max_profit([7, 1, 5, 3, 6, 4]) == 7
    assert max_profit([1, 2, 3, 4, 5]) == 4
    assert max_profit([7, 6, 4, 3, 1]) == 0
    assert max_profit([1]) == 0
    assert max_profit([]) == 0
    print('✅ LeetCode 122 (买卖股票 II) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 122. 买卖股票的最佳时机 II {'*' * 12}", sep='', end='\n\n')
    print(max_profit([7, 1, 5, 3, 6, 4]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
