"""
[题目编号]: LeetCode 1480. 一维数组的动态和 (Running Sum of 1d Array)
[难度]: Easy
[所属专题]: 00_warmup_basics
[前置知识]: 00_interview/gaosi (for 循环累加)、列表下标与 append

一、题目描述
给你一个数组 `nums`，请你计算「动态和」（即到当前位置为止的累计和）：
running_sum[i] = nums[0] + nums[1] + ... + nums[i]

示例:
- 输入: nums = [1, 2, 3, 4]
- 输出: [1, 3, 6, 10]  (解释: [1, 1+2, 1+2+3, 1+2+3+4])
- 边界: 空列表 [] -> []；单元素 [5] -> [5]；包含负数 [-1, 2, -3] -> [-1, 1, -2]

二、解法对比与复杂度
1. 解法一（新手直观累加版，不修改原列表）:
   - 思路: 准备一个累加器 `total = 0`，每遍历一个数字就加进 `total`，再追加到新列表。
   - 时间复杂度: O(n)，只遍历一遍数组。
   - 空间复杂度: O(n)，用于存放新返回的结果列表。
2. 解法二（标准库 itertools.accumulate Pythonic 版）:
   - 思路: Python 标准库 `itertools.accumulate` 专门用于计算累计结果。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 数据分析 / BI 报表: 计算「月度累计营收 (YTD)」「累计新增用户数」。
- 算法底层: 这就是大名鼎鼎的**前缀和 (Prefix Sum)** 思想原型，在区间求和、注意力掩码/概率累积分布采样（Top-p / Nucleus Sampling）中都会用到。
"""

from __future__ import annotations

from itertools import accumulate


def running_sum_basic(nums: list[int]) -> list[int]:
    """解法一：新手直观版，用 total 累加，逻辑和高斯求和完全一致。"""
    result: list[int] = []  # 用来保存每一步的累计和
    total = 0  # 注意：不要把变量命名为 sum，以免覆盖 Python 内置函数 sum()

    for num in nums:
        total += num  # 把当前元素累加进来
        result.append(total)  # 记录到当前位置为止的动态和

    return result


def running_sum_pythonic(nums: list[int]) -> list[int]:
    """解法二：Pythonic 版，直接调用标准库 itertools.accumulate。"""
    return list(accumulate(nums))


def run_tests() -> None:
    """自动化断言测试，覆盖普通用例与边界用例。"""
    cases = [
        ([1, 2, 3, 4], [1, 3, 6, 10]),
        ([1, 1, 1, 1, 1], [1, 2, 3, 4, 5]),
        ([3, 1, 2, 10, 1], [3, 4, 6, 16, 17]),
        ([], []),
        ([5], [5]),
        ([-1, 2, -3], [-1, 1, -2]),
    ]
    for solver in (running_sum_basic, running_sum_pythonic):
        for nums, expected in cases:
            actual = solver(nums)
            assert actual == expected, f'{solver.__name__} 失败: 输入={nums}, 实际={actual}, 期望={expected}'
    print('✅ LeetCode 1480 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 1480. 一维数组的动态和 {'*' * 12}", sep='', end='\n\n')
    sample = [1, 2, 3, 4]
    print(f'输入数组: {sample}')
    print(f'动态和结果: {running_sum_basic(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
