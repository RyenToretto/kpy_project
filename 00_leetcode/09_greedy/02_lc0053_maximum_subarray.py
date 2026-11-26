"""
[题目编号]: LeetCode 53. 最大子数组和 (Maximum Subarray / Kadane)
[难度]: Medium (贪心与一维 DP 同构的经典模板)
[所属专题]: 09_greedy
[前置知识]: 一维遍历、`max`、负收益取舍

一、题目描述
给你一个整数数组 `nums`，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。

示例:
- 输入: nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4] -> 输出: 6 (子数组 [4, -1, 2, 1])
- 输入: nums = [1] -> 输出: 1
- 输入: nums = [5, 4, -1, 7, 8] -> 输出: 23
- 边界: 全负数 [-3, -1, -2] -> -1（必须至少选一个）

二、解法对比与复杂度
1. 解法一（暴力枚举所有子数组）:
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(1)
2. 解法二（Kadane 贪心 / 一维 DP）:
   - 思路: 维护「以当前位置结尾」的最大连续和 `curr`。
     若上一轮 `curr` 已经是负数，它对下一轮只会造成拖累，直接丢弃，从当前元素重新开窗：
     `curr = max(num, curr + num)`；同时用 `best` 记录全局最大值。
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 时序指标峰值区间: 股票/CPU/延迟曲线上找「累计收益最高」的连续时段；异常检测里定位贡献最大的连续窗口。
"""

from __future__ import annotations


def max_subarray_bruteforce(nums: list[int]) -> int:
    """解法一：枚举起点终点累加，O(n^2) 直观对照。"""
    if not nums:
        raise ValueError('nums 不能为空')
    best = nums[0]
    n = len(nums)
    for start in range(n):
        acc = 0
        for end in range(start, n):
            acc += nums[end]
            best = max(best, acc)
    return best


def max_subarray_kadane(nums: list[int]) -> int:
    """解法二：Kadane 算法，单遍 O(n) / O(1)。"""
    if not nums:
        raise ValueError('nums 不能为空')
    curr = best = nums[0]
    for num in nums[1:]:
        # 前面一段如果已经是负贡献，就丢掉重开；否则继续累加
        curr = max(num, curr + num)
        best = max(best, curr)
    return best


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
        ([1], 1),
        ([5, 4, -1, 7, 8], 23),
        ([-3, -1, -2], -1),
        ([0, -1, 0], 0),
    ]
    for solver in (max_subarray_bruteforce, max_subarray_kadane):
        for nums, expected in cases:
            assert solver(nums) == expected, f'{solver.__name__} 失败: {nums}'
    try:
        max_subarray_kadane([])
    except ValueError:
        pass
    else:
        raise AssertionError('空数组必须报错')
    print('✅ LeetCode 53 (Kadane 最大子数组和) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 53. 最大子数组和 {'*' * 12}", sep='', end='\n\n')
    sample = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    print(f'{sample} -> 最大连续和: {max_subarray_kadane(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
