"""
[题目编号]: LeetCode 209. 长度最小的子数组 (Minimum Size Subarray Sum)
[难度]: Medium (正数数组上的最短滑窗模板)
[所属专题]: 03_sliding_window
[前置知识]: 03_sliding_window/01_lc0003、同向双指针

一、题目描述
给定正整数数组 `nums` 和正整数 `target`，找出满足和 `>= target` 的长度最小的连续子数组，返回其长度；不存在则返回 0。

示例:
- 输入: target = 7, nums = [2, 3, 1, 2, 4, 3] -> 2 ([4, 3])
- 输入: target = 4, nums = [1, 4, 4] -> 1
- 边界: 总和仍 < target -> 0

为什么能滑窗？数组全是正数，右扩必增、左缩必减，满足单调性。含负数时改用前缀和+哈希（见 LC 560）。

二、解法对比
1. 暴力枚举: O(n^2)
2. 同向双指针滑窗: O(n) —— `right` 扩张累加，一旦 `acc >= target` 就尽量收缩 `left` 并更新最短长度

三、工程映射
- 最小窗口达标: 日志流量/延迟累计首次达到阈值的最短时段；批处理「凑够一批数据」的最短缓冲长度。
"""

from __future__ import annotations


def min_subarray_len_bruteforce(target: int, nums: list[int]) -> int:
    """解法一：枚举所有子数组，O(n^2)。"""
    n = len(nums)
    best = n + 1
    for start in range(n):
        acc = 0
        for end in range(start, n):
            acc += nums[end]
            if acc >= target:
                best = min(best, end - start + 1)
                break
    return 0 if best == n + 1 else best


def min_subarray_len_window(target: int, nums: list[int]) -> int:
    """解法二：正数滑窗，O(n)。"""
    left = 0
    acc = 0
    best = len(nums) + 1
    for right, num in enumerate(nums):
        acc += num
        while acc >= target and left <= right:
            best = min(best, right - left + 1)
            acc -= nums[left]
            left += 1
    return 0 if best == len(nums) + 1 else best


def run_tests() -> None:
    cases = [
        (7, [2, 3, 1, 2, 4, 3], 2),
        (4, [1, 4, 4], 1),
        (11, [1, 1, 1, 1, 1, 1, 1, 1], 0),
        (15, [1, 2, 3, 4, 5], 5),
        (1, [1], 1),
    ]
    for solver in (min_subarray_len_bruteforce, min_subarray_len_window):
        for target, nums, expected in cases:
            assert solver(target, nums) == expected, f'{solver.__name__} 失败'
    print('✅ LeetCode 209 (最短正数滑窗) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 209. 长度最小的子数组 {'*' * 12}", sep='', end='\n\n')
    print(min_subarray_len_window(7, [2, 3, 1, 2, 4, 3]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
