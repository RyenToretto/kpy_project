"""
[题目编号]: LeetCode 198. 打家劫舍 (House Robber)
[难度]: Medium (相邻约束一维 DP 标准第一题)
[所属专题]: 10_dynamic_programming
[前置知识]: 10_dynamic_programming/00_lc0070_climbing_stairs、滚动变量

一、题目描述
你是一名专业的小偷，计划偷窃沿街的房屋。每间房内都藏有一定的现金。
约束：相邻的房屋装有防盗系统，**如果两间相邻的房屋在同一晚上被闯入，系统会自动报警**。
给定一个代表每个房屋存放金额的非负整数数组 `nums`，计算你在不触动警报装置的情况下，一夜之内能够偷窃到的最高金额。

示例:
- 输入: nums = [1, 2, 3, 1] -> 输出: 4 (偷第 1、3 间)
- 输入: nums = [2, 7, 9, 3, 1] -> 输出: 12 (偷第 1、3、5 间)
- 边界: [] -> 0；[5] -> 5；[2, 1] -> 2

二、解法对比与复杂度
核心转移：走到第 `i` 间时，只有两种选择——
- 偷第 `i` 间：则第 `i-1` 间不能偷，金额 = `dp[i-2] + nums[i]`
- 不偷第 `i` 间：金额 = `dp[i-1]`
取两者较大值：`dp[i] = max(dp[i-1], dp[i-2] + nums[i])`

1. 解法一（DP 数组）: 时间 O(n)，空间 O(n)
2. 解法二（滚动两个变量）: 时间 O(n)，空间 O(1)

与爬楼梯的区别：爬楼梯是「到达方式计数」，本题是「带相邻互斥约束的最优收益」。

三、工程与 AI/大数据实战映射
- 资源排班 / 隔位采样: 相邻任务不能同时占用同一资源时的最大收益排程；传感器隔点采样最大化信息量。
"""

from __future__ import annotations


def rob_dp_array(nums: list[int]) -> int:
    """解法一：一维 DP 数组，便于看清转移。"""
    n = len(nums)
    if n == 0:
        return 0
    if n == 1:
        return nums[0]
    dp = [0] * n
    dp[0] = nums[0]
    dp[1] = max(nums[0], nums[1])
    for i in range(2, n):
        dp[i] = max(dp[i - 1], dp[i - 2] + nums[i])
    return dp[-1]


def rob_rolling(nums: list[int]) -> int:
    """解法二：只保留前两间的最优结果，空间 O(1)。"""
    prev2 = 0  # dp[i-2]
    prev1 = 0  # dp[i-1]
    for money in nums:
        curr = max(prev1, prev2 + money)
        prev2, prev1 = prev1, curr
    return prev1


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([1, 2, 3, 1], 4),
        ([2, 7, 9, 3, 1], 12),
        ([2, 1], 2),
        ([5], 5),
        ([], 0),
        ([0, 0, 0], 0),
        ([10, 1, 1, 10], 20),
    ]
    for solver in (rob_dp_array, rob_rolling):
        for nums, expected in cases:
            assert solver(nums) == expected, f'{solver.__name__} 失败: {nums}'
    print('✅ LeetCode 198 (打家劫舍) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 198. 打家劫舍 {'*' * 12}", sep='', end='\n\n')
    sample = [2, 7, 9, 3, 1]
    print(f'{sample} -> 最高金额: {rob_rolling(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
