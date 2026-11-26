"""
[题目编号]: LeetCode 215. 数组中的第K个最大元素 (Kth Largest Element in an Array)
[难度]: Medium (大厂常考 Top-K 原型题)
[所属专题]: 11_heap_and_trie
[前置知识]: heapq 小顶堆、random.choice 快速选择

一、题目描述
给定整数数组 `nums` 和整数 `k`，请返回数组中第 `k` 个最大的元素（请注意，是排序后的第 `k` 个最大元素，而不是第 `k` 个不同的元素）。

示例:
- 输入: nums = [3, 2, 1, 5, 6, 4], k = 2 -> 输出: 5
- 输入: nums = [3, 2, 3, 1, 2, 4, 5, 5, 6], k = 4 -> 输出: 4
- 边界: [1], k=1 -> 1；大量重复元素 [5]*1000, k=500 -> 5

二、解法对比与复杂度
1. 解法一（容量为 k 的小顶堆 - 流式大数据稳如泰山）:
   - 思路: 维护一个最多 `k` 个元素的小顶堆。每来一个新数就进堆；一旦超过 `k` 个，就把最小（最弱）的堆顶弹出。最后堆顶剩下的正好是「前 k 大里面最小的那一个」，即第 `k` 大！
   - 时间复杂度: O(n log k)
   - 空间复杂度: O(k)（哪怕有 10 亿条日志流式过来，内存也只占 k 个！）
2. 解法二（三路划分快速选择 Quickselect 简洁版 - 期望 O(n)）:
   - 思路: 随机选基准 `pivot`，把数组分成 `> pivot`、`== pivot`、`< pivot` 三段（三路划分可以完美防止大量重复元素退化成 O(n^2)！），只去包含第 k 大的那一段继续递归。
   - 时间复杂度: 期望 O(n)
   - 空间复杂度: O(n)（列表推导新建切片，易读但不算原地）
3. 解法三（原地三路划分 Quickselect 极限优化版 - 期望 O(n) + O(1) 空间）:
   - 思路: 参考荷兰国旗三指针 (`lt`, `mid`, `gt`) 在原数组上直接切分三段，并用 `while` 循环代替尾递归，不额外申请切片内存。
   - 时间复杂度: 期望 O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 大数据 Top-K 算子: Spark / Flink 中求延迟 P99、活跃用户 Top-K，不可能把 TB 级数据全拉进单机排序，而是各个分片用容量为 K 的堆各自筛出 Top-K 后再归并！
"""

from __future__ import annotations

import heapq
import random


def find_kth_largest_heap(nums: list[int], k: int) -> int:
    """解法一：维护大小为 k 的小顶堆，适合流式数据与面试稳妥作答。"""
    min_heap: list[int] = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]


def find_kth_largest_quickselect(nums: list[int], k: int) -> int:
    """解法二：三路随机快速选择，期望时间 O(n)，且不怕全重复数组。"""
    def quickselect(arr: list[int], target_k: int) -> int:
        pivot = random.choice(arr)
        greater = [x for x in arr if x > pivot]
        equal = [x for x in arr if x == pivot]
        smaller = [x for x in arr if x < pivot]

        if target_k <= len(greater):
            return quickselect(greater, target_k)
        if target_k <= len(greater) + len(equal):
            return pivot
        return quickselect(smaller, target_k - len(greater) - len(equal))

    return quickselect(nums, k)


def find_kth_largest_quickselect_inplace(nums: list[int], k: int) -> int:
    """解法三：原地三路划分快速选择（循环版），期望时间 O(n)、额外空间 O(1)。"""
    arr = nums[:]  # 复制一份防止污染外部传入的测试用例列表
    target_idx = k - 1
    left, right = 0, len(arr) - 1

    while left <= right:
        pivot = arr[random.randint(left, right)]
        # 荷兰国旗三路划分（降序）：[left..lt-1] > pivot, [lt..gt] == pivot, [gt+1..right] < pivot
        lt, mid, gt = left, left, right
        while mid <= gt:
            if arr[mid] > pivot:
                arr[lt], arr[mid] = arr[mid], arr[lt]
                lt += 1
                mid += 1
            elif arr[mid] < pivot:
                arr[mid], arr[gt] = arr[gt], arr[mid]
                gt -= 1
            else:
                mid += 1

        if lt <= target_idx <= gt:
            return arr[target_idx]
        if target_idx < lt:
            right = lt - 1
        else:
            left = gt + 1

    raise ValueError(f'非法 k={k}')


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([3, 2, 1, 5, 6, 4], 2, 5),
        ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, 4),
        ([1], 1, 1),
        ([5] * 200, 100, 5),
        ([-1, -5, 0, 3, 2], 5, -5),
    ]
    for solver in (find_kth_largest_heap, find_kth_largest_quickselect, find_kth_largest_quickselect_inplace):
        for nums, k, expected in cases:
            assert solver(nums, k) == expected, f'{solver.__name__} 失败: k={k}'
    print('✅ LeetCode 215 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 215. 数组中的第K个最大元素 {'*' * 12}", sep='', end='\n\n')
    sample = [3, 2, 1, 5, 6, 4]
    print(f'{sample} 中第 2 大元素 = {find_kth_largest_heap(sample, 2)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
