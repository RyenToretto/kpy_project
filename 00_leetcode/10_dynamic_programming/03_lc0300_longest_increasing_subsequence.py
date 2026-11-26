"""
[题目编号]: LeetCode 300. 最长递增子序列 (Longest Increasing Subsequence / LIS)
[难度]: Medium (DP 过渡到贪心二分的里程碑经典题，参考 kamyu104 bisect 写法重写为 Python 3.12 教学版)
[所属专题]: 10_dynamic_programming
[前置知识]: 05_binary_search (`bisect_left`)、一维 DP 数组定义

一、题目描述
给你一个整数数组 `nums`，找到其中**最长严格递增子序列**的长度（注意：子序列不要求连续，只需保持原顺序）。

示例:
- 输入: nums = [10, 9, 2, 5, 3, 7, 101, 18] -> 输出: 4 (例如 [2, 3, 7, 101])
- 输入: nums = [0, 1, 0, 3, 2, 3] -> 输出: 4
- 输入: nums = [7, 7, 7, 7] -> 输出: 1 (严格递增，相等不算递增)
- 边界: [] -> 0；[5] -> 1

二、解法对比与复杂度
1. 解法一（经典动态规划 - 必会基础模板）:
   - 思路: 定义 `dp[i]` = **以 `nums[i]` 结尾**的最长递增子序列长度（初始全为 1）。
     枚举它前面的每个 `j < i`，只要 `nums[j] < nums[i]`，就能接在 `j` 后面：`dp[i] = max(dp[i], dp[j] + 1)`。最后取 `max(dp)`。
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(n)
2. 解法二（贪心 + 二分查找 `tails` 数组 - 性能跃迁最优解）:
   - 思路: 维护数组 `tails`，其中 `tails[k]` 表示「所有长度为 `k+1` 的递增子序列里，**末尾元素最小**可以是多少」。
     为什么要让末尾元素尽量小？因为**尾巴越小，后面能接上的数字就越多**！
     遍历每个 `num`：用 `bisect_left(tails, num)` 找到第一个 `>= num` 的位置 `pos`：
     - 如果 `pos == len(tails)`，说明 `num` 比所有已有尾巴都大，可以直接延长最长序列：`tails.append(num)`；
     - 否则把 `tails[pos]` 替换成更小的 `num`（保持长度不变但潜力更大）。
     注意：`tails` 最终长度就是 LIS 长度（但 `tails` 本身的元素未必是一条合法原序列）。
   - 时间复杂度: O(n log n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- **重排一致性与增量序列提取**: 在检索重排结果一致性校验、推荐系统用户点击序列演化、软件版本号兼容链查找与 Diff 对齐（Myers Diff 核心正是找最长公共子序列 / LIS）中广泛使用。
"""

from __future__ import annotations

from bisect import bisect_left


def length_of_lis_dp(nums: list[int]) -> int:
    """解法一：标准一维 DP，时间 O(n^2)，直观好推导出转移方程。"""
    if not nums:
        return 0
    dp = [1] * len(nums)

    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)


def length_of_lis_binary_search(nums: list[int]) -> int:
    """解法二：贪心维护最小末尾序列 tails + bisect_left 二分替换，时间 O(n log n)。"""
    tails: list[int] = []
    for num in nums:
        # 严格递增：找第一个 >= num 的位置（非严格递增才用 bisect_right）
        pos = bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([10, 9, 2, 5, 3, 7, 101, 18], 4),
        ([0, 1, 0, 3, 2, 3], 4),
        ([7, 7, 7, 7], 1),
        ([1, 2, 3, 4, 5], 5),
        ([5, 4, 3, 2, 1], 1),
        ([42], 1),
        ([], 0),
    ]
    for solver in (length_of_lis_dp, length_of_lis_binary_search):
        for nums, expected in cases:
            actual = solver(nums)
            assert actual == expected, f'{solver.__name__} 失败: {nums} -> {actual}'
    print('✅ LeetCode 300 (LIS) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 300. 最长递增子序列 {'*' * 12}", sep='', end='\n\n')
    sample = [10, 9, 2, 5, 3, 7, 101, 18]
    print(f'数组 {sample} 的最长严格递增子序列长度 = {length_of_lis_binary_search(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
