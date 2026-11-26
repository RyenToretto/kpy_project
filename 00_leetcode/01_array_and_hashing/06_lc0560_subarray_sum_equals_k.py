"""
[题目编号]: LeetCode 560. 和为 K 的子数组 (Subarray Sum Equals K)
[难度]: Medium (前缀和 + 哈希表第一经典模板，参考 kamyu104 最优模板重写为 Python 3.12 教学版)
[所属专题]: 01_array_and_hashing
[前置知识]: 00_warmup_basics/00_lc1480_running_sum (前缀和)、01_array_and_hashing/00_lc0001_two_sum (哈希配对)、defaultdict

一、题目描述
给你一个整数数组 `nums`（可能包含**负数和 0**）和一个整数 `k`，请你统计并返回该数组中和为 `k` 的**连续子数组**的个数。

示例:
- 输入: nums = [1, 1, 1], k = 2 -> 输出: 2 ([1, 1] 和第二个 [1, 1])
- 输入: nums = [1, 2, 3], k = 3 -> 输出: 2 ([1, 2] 和 [3])
- 边界: 含负数 [1, -1, 0], k = 0 -> 输出: 3 ([1, -1], [0], [1, -1, 0])；空数组 [] -> 0

为什么不能用滑动窗口？因为数组里**允许有负数**！窗口右扩时和不一定变大，左缩时和不一定变小，不满足单调性。

二、解法对比与复杂度
1. 解法一（暴力枚举所有子数组起点与终点）:
   - 思路: 外层固定起点 `i`，内层向后累加 `acc` 到终点 `j`，每当 `acc == k` 就计数 +1。
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(1)
2. 解法二（前缀和 + 哈希表，等同「在前缀和序列上做 Two Sum 计数」）:
   - 思路: 设前 `i` 项累加和为 `prefix`。若之前某个位置的前缀和等于 `prefix - k`，那么这两个位置中间那一段子数组的和恰好就是 `prefix - (prefix - k) = k`！
     用哈希表 `prefix_counts` 实时记录每种前缀和出现过多少次。
     **最关键的边界初始化**：`prefix_counts[0] = 1`（代表「什么元素都不选」时前缀和为 0 出现 1 次，否则从下标 0 开始恰好等于 `k` 的子数组会被漏掉）。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 时序指标与日志异常窗口统计: 在带正负波动的资金流水（入金/出金）、传感器净增量流中，统计「恰好净变化为目标值 K 的连续时段数量」，只需单遍扫描即可在线完成。
"""

from __future__ import annotations

from collections import defaultdict


def subarray_sum_bruteforce(nums: list[int], k: int) -> int:
    """解法一：枚举起点与终点累加，O(n^2) 直观对照版。"""
    count = 0
    n = len(nums)
    for start in range(n):
        acc = 0
        for end in range(start, n):
            acc += nums[end]
            if acc == k:
                count += 1
    return count


def subarray_sum_prefix_hash(nums: list[int], k: int) -> int:
    """解法二：前缀和 + 哈希表记录历史前缀和频次，O(n) 最优解。"""
    prefix_counts: dict[int, int] = defaultdict(int)
    prefix_counts[0] = 1  # 空前缀和为 0，确保从 index=0 起步的子数组能被正确统计

    acc = 0
    count = 0
    for num in nums:
        acc += num
        # 如果之前出现过 prefix == acc - k，说明中间这段子数组和正好为 k
        count += prefix_counts[acc - k]
        # 必须先统计再存入当前 acc（尤其是 k == 0 时，避免自己和自己配对）
        prefix_counts[acc] += 1

    return count


def run_tests() -> None:
    """自动化断言测试，覆盖正数、负数、零、单元素与空数组。"""
    cases = [
        ([1, 1, 1], 2, 2),
        ([1, 2, 3], 3, 2),
        ([1, -1, 0], 0, 3),
        ([0, 0, 0], 0, 6),
        ([3], 3, 1),
        ([3], 5, 0),
        ([], 0, 0),
    ]
    for solver in (subarray_sum_bruteforce, subarray_sum_prefix_hash):
        for nums, k, expected in cases:
            actual = solver(nums, k)
            assert actual == expected, f'{solver.__name__} 失败: nums={nums}, k={k}, 实际={actual}'
    print('✅ LeetCode 560 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 560. 和为 K 的子数组 {'*' * 12}", sep='', end='\n\n')
    sample = [1, -1, 0, 2, -2, 2]
    print(f'数组: {sample}, 目标 k=2 -> 满足条件的连续子数组个数: {subarray_sum_prefix_hash(sample, 2)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
