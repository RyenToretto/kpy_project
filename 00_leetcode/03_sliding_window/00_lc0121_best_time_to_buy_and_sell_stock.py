"""
[题目编号]: LeetCode 121. 买卖股票的最佳时机 (Best Time to Buy and Sell Stock)
[难度]: Easy
[所属专题]: 03_sliding_window
[前置知识]: for 循环、min() / max()

一、题目描述
给定一个数组 `prices`，它的第 `i` 个元素 `prices[i]` 表示一支给定股票第 `i` 天的价格。
你只能选择**某一天**买入这只股票，并选择在**未来的某一个不同的日子**卖出。返回你能获取的最大利润；如果不能获利，返回 `0`。

示例:
- 输入: [7, 1, 5, 3, 6, 4] -> 输出: 5 (第 2 天价格 1 买入，第 5 天价格 6 卖出，6 - 1 = 5)
- 输入: [7, 6, 4, 3, 1] -> 输出: 0
- 边界: [] -> 0；[5] -> 0

二、解法对比与复杂度
1. 解法一（暴力枚举所有买入卖出日组合 - O(n^2)）:
   - 思路: 枚举所有 `i < j` 的组合计算 `prices[j] - prices[i]`。
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(1)
2. 解法二（一次遍历：维护历史最低价 - O(n) 最优）:
   - 思路: 想象你每天站在当天回望过去——如果今天卖出，要想赚最多，买入日一定是「今天之前的历史最低价 `min_price`」！一边向右移动一边刷新 `min_price` 和 `max_profit` 即可。
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 量化分析 / 时序指标最大回撤与最大收益窗口: 扫描金融 K 线或系统延迟曲线，在单遍流式读取中算出局部极值差，不需要回溯历史全量数组。
"""

from __future__ import annotations


def max_profit_bruteforce(prices: list[int]) -> int:
    """解法一：暴力双循环枚举买入与卖出日，数据大时会超时，仅作对照。"""
    best = 0
    n = len(prices)
    for buy_day in range(n):
        for sell_day in range(buy_day + 1, n):
            profit = prices[sell_day] - prices[buy_day]
            if profit > best:
                best = profit
    return best


def max_profit_one_pass(prices: list[int]) -> int:
    """解法二：一次遍历维护历史最低买入价与当前最大利润。"""
    if len(prices) < 2:
        return 0

    min_price = prices[0]
    max_profit = 0

    for price in prices[1:]:
        # 如果今天卖出，利润就是今天价格减去此前遇到过的最低价格
        max_profit = max(max_profit, price - min_price)
        # 更新历史最低价，给未来的日子作为参考买入价
        min_price = min(min_price, price)

    return max_profit


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([7, 1, 5, 3, 6, 4], 5),
        ([7, 6, 4, 3, 1], 0),
        ([2, 4, 1], 2),
        ([5], 0),
        ([], 0),
    ]
    for solver in (max_profit_bruteforce, max_profit_one_pass):
        for prices, expected in cases:
            assert solver(prices) == expected, f'{solver.__name__} 失败: {prices}'
    print('✅ LeetCode 121 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 121. 买卖股票的最佳时机 {'*' * 12}", sep='', end='\n\n')
    sample = [7, 1, 5, 3, 6, 4]
    print(f'股价序列: {sample}, 最大利润: {max_profit_one_pass(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
