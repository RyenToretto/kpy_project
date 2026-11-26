"""
[题目编号]: LeetCode 739. 每日温度 (Daily Temperatures)
[难度]: Medium (单调栈第一标准模板题)
[所属专题]: 04_stack_and_queue
[前置知识]: list 栈操作、enumerate()

一、题目描述
给定一个整数数组 `temperatures`，表示每天的温度，返回一个数组 `answer`：
`answer[i]` 是指对于第 `i` 天，**下一个更高温度**出现在几天后。如果气温在这之后都不会升高，请在该位置用 `0` 代替。

示例:
- 输入: temperatures = [73, 74, 75, 71, 69, 72, 76, 73]
- 输出: [1, 1, 4, 2, 1, 1, 0, 0]
- 边界: 递减序列 [80, 70, 60] -> [0, 0, 0]；递增 [30, 40, 50] -> [1, 1, 0]

二、解法对比与复杂度
1. 解法一（暴力向右找第一个更大的值）:
   - 思路: 对每一天 `i` 往右挨个找第一天 `temperatures[j] > temperatures[i]`。
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(1)
2. 解法二（单调递减栈存下标 - O(n) 核心模板）:
   - 思路: 栈里存「还没找到比自己更暖和那天」的**历史日子下标**，栈内对应温度保持**从栈底到栈顶递减**。
     当新的一天 `i` 温度更高时，说明栈顶那些比今天冷的日子「终于等到了更暖和的一天」，不断弹出栈顶 `prev_day` 并结算 `answer[prev_day] = i - prev_day`！
   - 时间复杂度: O(n)，每个下标最多入栈一次、出栈一次。
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 金融量化与信号突破: 在股票/监控指标流中，求「每根 K 线之后多少天首次突破前高 / 突破阈值」，用单调栈只需单遍 O(n) 扫描即可完成。
"""

from __future__ import annotations


def daily_temperatures_bruteforce(temperatures: list[int]) -> list[int]:
    """解法一：暴力二重循环，方便与单调栈对比。"""
    n = len(temperatures)
    answer = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if temperatures[j] > temperatures[i]:
                answer[i] = j - i
                break
    return answer


def daily_temperatures_monotonic_stack(temperatures: list[int]) -> list[int]:
    """解法二：单调递减栈（存下标），O(n) 解决「下一个更大元素」类问题。"""
    answer = [0] * len(temperatures)
    stack: list[int] = []  # 存放尚未找到升温日的下标

    for day, temp in enumerate(temperatures):
        # 只要今天的温度比栈顶那天高，栈顶那天的答案就确定了
        while stack and temp > temperatures[stack[-1]]:
            prev_day = stack.pop()
            answer[prev_day] = day - prev_day
        stack.append(day)

    return answer


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([73, 74, 75, 71, 69, 72, 76, 73], [1, 1, 4, 2, 1, 1, 0, 0]),
        ([30, 40, 50, 60], [1, 1, 1, 0]),
        ([80, 70, 60], [0, 0, 0]),
        ([30], [0]),
        ([], []),
    ]
    for solver in (daily_temperatures_bruteforce, daily_temperatures_monotonic_stack):
        for temps, expected in cases:
            assert solver(temps) == expected, f'{solver.__name__} 失败: {temps}'
    print('✅ LeetCode 739 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 739. 每日温度 {'*' * 12}", sep='', end='\n\n')
    sample = [73, 74, 75, 71, 69, 72, 76, 73]
    print(f'温度序列: {sample}')
    print(f'等待升温天数: {daily_temperatures_monotonic_stack(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
