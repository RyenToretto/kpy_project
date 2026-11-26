"""
[题目编号]: LeetCode 347. 前 K 个高频元素 (Top K Frequent Elements)
[难度]: Medium
[所属专题]: 01_array_and_hashing
[前置知识]: collections.Counter、heapq (小顶堆)、桶排序思想

一、题目描述
给你一个整数数组 `nums` 和一个整数 `k`，请你返回其中出现频率前 `k` 高的元素（可以按任意顺序返回）。
题目要求算法时间复杂度必须优于 O(n log n)。

示例:
- 输入: nums = [1, 1, 1, 2, 2, 3], k = 2
- 输出: [1, 2]
- 边界: [1], k=1 -> [1]；全部相同 [5, 5, 5], k=1 -> [5]

二、解法对比与复杂度
1. 解法一（最小堆版 - O(n log k)，海量流式数据最常用）:
   - 思路: 先用 `Counter` 统计频次；然后维护一个**容量仅为 k 的小顶堆**。每次遇到 `(freq, num)` 就压入堆，若堆大小超过 `k` 就把堆顶（目前最弱的那个）踢出去！最终堆里留下的就是前 `k` 强。
   - 时间复杂度: O(n log k)
   - 空间复杂度: O(n)
2. 解法二（桶排序 Bucket Sort 版 - O(n) 极限最优）:
   - 思路: 每个数字出现次数最多不超过 `len(nums)`！所以准备 `len(nums) + 1` 个桶，`buckets[freq]` 存放「恰好出现 freq 次的所有数字」，最后从高频桶倒序往回捡满 k 个即可。
   - 时间复杂度: O(n)，彻底摆脱 log 因子！
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 大数据高频经典题: 搜索热词榜 Top-100、日志异常 IP Top-10、RAG 混合检索重排 (Rerank) 后取 Top-K 文档切片，都是这道题的直接变体！
"""

from __future__ import annotations

import heapq
from collections import Counter


def top_k_frequent_heap(nums: list[int], k: int) -> list[int]:
    """解法一：小顶堆维护前 K 大元素，O(n log k)，非常节省堆内存。"""
    if k <= 0 or not nums:
        return []

    counts = Counter(nums)
    min_heap: list[tuple[int, int]] = []  # 堆元素为 (出现次数, 数值)，按次数比较大小

    for num, freq in counts.items():
        heapq.heappush(min_heap, (freq, num))
        if len(min_heap) > k:
            # 踢掉堆顶（频次最小的那一个），保证堆里永远只留最大的 k 个
            heapq.heappop(min_heap)

    return [num for _, num in min_heap]


def top_k_frequent_bucket(nums: list[int], k: int) -> list[int]:
    """解法二：频次桶排序，时间复杂度 O(n)。"""
    if k <= 0 or not nums:
        return []

    counts = Counter(nums)
    # buckets[freq] 保存所有出现次数恰好等于 freq 的数字
    buckets: list[list[int]] = [[] for _ in range(len(nums) + 1)]
    for num, freq in counts.items():
        buckets[freq].append(num)

    result: list[int] = []
    # 从最高频次倒着往低频次桶里收集，收够 k 个立刻停止
    for freq in range(len(buckets) - 1, 0, -1):
        for num in buckets[freq]:
            result.append(num)
            if len(result) == k:
                return result

    return result


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([1, 1, 1, 2, 2, 3], 2, {1, 2}),
        ([1], 1, {1}),
        ([4, 1, -1, 2, -1, 2, 3], 2, {-1, 2}),
        ([5, 5, 5], 1, {5}),
    ]
    for solver in (top_k_frequent_heap, top_k_frequent_bucket):
        for nums, k, expected_set in cases:
            actual = solver(nums, k)
            assert set(actual) == expected_set and len(actual) == k, f'{solver.__name__} 失败: {actual}'
    print('✅ LeetCode 347 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 347. 前 K 个高频元素 {'*' * 12}", sep='', end='\n\n')
    nums, k = [1, 1, 1, 2, 2, 3], 2
    print(f'输入: nums={nums}, k={k}')
    print(f'桶排序 O(n) 结果: {top_k_frequent_bucket(nums, k)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
