"""
[题目编号]: LeetCode 4. 寻找两个正序数组的中位数 (Median of Two Sorted Arrays)
[难度]: Hard (划分子数组的二分答案)
[所属专题]: 05_binary_search
[前置知识]: 05_binary_search/00_lc0704、有序数组合并直觉

一、题目描述
给定两个大小分别为 `m` 和 `n` 的正序（从小到大）数组 `nums1` 和 `nums2`。请找出并返回这两个正序数组的中位数。
算法时间复杂度应是 O(log (m+n))。

示例:
- [1, 3], [2] -> 2.0
- [1, 2], [3, 4] -> 2.5
- [], [1] -> 1.0

二、解法对比
1. 合并后再取中位: O(m+n) 时间，不满足进阶复杂度。
2. 在较短数组上二分切割点:
   - 目标: 把两数组一起分成左半 / 右半，使左侧个数 = (m+n+1)//2，且左侧最大值 <= 右侧最小值。
   - 在短数组上二分 `i`（nums1 左边拿几个），则 nums2 左边拿 `j = half - i`。
   - 若 `nums1[i-1] > nums2[j]`：`i` 太大，右缩；若 `nums2[j-1] > nums1[i]`：`i` 太小，左扩。
   - 时间 O(log(min(m, n)))，空间 O(1)

三、工程映射
- 有序分片中位数 / 分位数: 两路已排序日志流不合并磁盘，直接二分定位全局中位数；多路有序分片的分位数查询同理。
"""

from __future__ import annotations


def find_median_merge(nums1: list[int], nums2: list[int]) -> float:
    """解法一：归并后取中位，O(m+n)。"""
    merged: list[int] = []
    i = j = 0
    while i < len(nums1) and j < len(nums2):
        if nums1[i] <= nums2[j]:
            merged.append(nums1[i])
            i += 1
        else:
            merged.append(nums2[j])
            j += 1
    merged.extend(nums1[i:])
    merged.extend(nums2[j:])
    n = len(merged)
    mid = n // 2
    if n % 2 == 1:
        return float(merged[mid])
    return (merged[mid - 1] + merged[mid]) / 2


def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    """解法二：在较短数组上二分切割点，O(log(min(m,n)))。"""
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    total = m + n
    half = (total + 1) // 2
    left, right = 0, m

    while left <= right:
        i = (left + right) // 2  # nums1 左边取 i 个
        j = half - i             # nums2 左边取 j 个
        left1 = nums1[i - 1] if i > 0 else float('-inf')
        right1 = nums1[i] if i < m else float('inf')
        left2 = nums2[j - 1] if j > 0 else float('-inf')
        right2 = nums2[j] if j < n else float('inf')

        if left1 <= right2 and left2 <= right1:
            if total % 2 == 1:
                return float(max(left1, left2))
            return (max(left1, left2) + min(right1, right2)) / 2
        if left1 > right2:
            right = i - 1
        else:
            left = i + 1
    raise ValueError('输入必须是两个已排序数组')


def run_tests() -> None:
    cases = [
        ([1, 3], [2], 2.0),
        ([1, 2], [3, 4], 2.5),
        ([], [1], 1.0),
        ([2], [], 2.0),
        ([0, 0], [0, 0], 0.0),
        ([1, 2, 5], [3, 4, 6, 7], 4.0),
    ]
    for solver in (find_median_merge, find_median_sorted_arrays):
        for a, b, expected in cases:
            actual = solver(a, b)
            assert abs(actual - expected) < 1e-9, f'{solver.__name__} 失败: {a},{b} -> {actual}'
    print('✅ LeetCode 4 (两有序数组中位数) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 4. 寻找两个正序数组的中位数 {'*' * 12}", sep='', end='\n\n')
    print(find_median_sorted_arrays([1, 2], [3, 4]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
