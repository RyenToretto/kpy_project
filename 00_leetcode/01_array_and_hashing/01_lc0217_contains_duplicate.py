"""
[题目编号]: LeetCode 217. 存在重复元素 (Contains Duplicate)
[难度]: Easy
[所属专题]: 01_array_and_hashing
[前置知识]: set (集合)、len()、排序 sorted()

一、题目描述
给你一个整数数组 `nums`。如果任一值在数组中出现**至少两次**，返回 `True`；如果每个元素互不相同，返回 `False`。

示例:
- 输入: [1, 2, 3, 1] -> True
- 输入: [1, 2, 3, 4] -> False
- 边界: [] -> False；[99] -> False；[0, 0] -> True

二、解法对比与复杂度
1. 解法一（排序对比相邻元素）:
   - 思路: 先排序 `sorted(nums)`，如果有重复元素，它们一定紧挨在一起。
   - 时间复杂度: O(n log n)
   - 空间复杂度: O(n)（`sorted` 会产生新列表；若原地 `nums.sort()` 为 O(1)~O(n)）
2. 解法二（集合渐进遍历 - 推荐）:
   - 思路: 用一个集合 `seen` 边遍历边记录，只要发现 `num in seen` 立刻提前返回 `True`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)
3. 解法三（Pythonic 长度比较一行版）:
   - 思路: 集合天然自动去重，直接比较 `len(set(nums)) != len(nums)`。简洁，但无法像解法二那样在刚遇到第一个重复时就提前退出。

三、工程与 AI/大数据实战映射
- RAG 知识库与数据清洗: 批量切分文档后做 URL / Chunk Hash 去重，核心就是把历史指纹放进 `set`（规模超亿级时再升级为布隆过滤器）。
"""

from __future__ import annotations


def contains_duplicate_sort(nums: list[int]) -> bool:
    """解法一：排序后检查相邻元素是否相等。"""
    ordered = sorted(nums)
    for i in range(1, len(ordered)):
        if ordered[i] == ordered[i - 1]:
            return True
    return False


def contains_duplicate_set(nums: list[int]) -> bool:
    """解法二：用集合边扫描边查重，遇到重复立即提前返回（实际工程最快）。"""
    seen: set[int] = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False


def contains_duplicate_pythonic(nums: list[int]) -> bool:
    """解法三：利用 set 去重后长度变化，一行搞定。"""
    return len(set(nums)) != len(nums)


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([1, 2, 3, 1], True),
        ([1, 2, 3, 4], False),
        ([1, 1, 1, 3, 3, 4, 3, 2, 4, 2], True),
        ([], False),
        ([99], False),
        ([-1, -1], True),
    ]
    for solver in (contains_duplicate_sort, contains_duplicate_set, contains_duplicate_pythonic):
        for nums, expected in cases:
            assert solver(nums) is expected, f'{solver.__name__} 失败: nums={nums}'
    print('✅ LeetCode 217 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 217. 存在重复元素 {'*' * 12}", sep='', end='\n\n')
    sample = [1, 2, 3, 1]
    print(f'{sample} 是否存在重复元素: {contains_duplicate_set(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
