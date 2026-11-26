"""
[题目编号]: LeetCode 1. 两数之和 (Two Sum)
[难度]: Easy
[所属专题]: 01_array_and_hashing
[前置知识]: for 循环、enumerate()、dict (哈希表)

一、题目描述
给定一个整数数组 `nums` 和一个目标值 `target`，请在数组中找出和为 `target` 的那两个整数，并返回它们的下标列表 `[i, j]`。
假设每种输入只会对应一个有效答案，且同一个元素在答案里不能重复出现。

示例:
- 输入: nums = [2, 7, 11, 15], target = 9
- 输出: [0, 1]  (因为 nums[0] + nums[1] == 2 + 7 == 9)
- 边界: 负数 [-3, 4, 3, 90], target=0 -> [0, 2]；相同数字 [3, 3], target=6 -> [0, 1]

二、解法对比与复杂度
1. 解法一（新手双层循环暴力版）:
   - 思路: 固定左边的数 `i`，再遍历它右边的每一个数 `j`，判断两数之和是否等于 `target`。
   - 时间复杂度: O(n^2)，数据量 1 万时要比较约 5000 万次。
   - 空间复杂度: O(1)
2. 解法二（一次遍历哈希表最优版）:
   - 思路: 遍历到当前数字 `num` 时，计算「还需要另一个什么数」`need = target - num`。
     直接去字典 `seen` 里 O(1) 查询 `need` 之前有没有出现过！如果出现过，直接返回 `[seen[need], i]`；没出现过就把当前 `seen[num] = i` 存下来给后面的数配对。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 空间换时间第一课: 这几乎是所有数据库 Hash Join（哈希连接）、用户行为日志关联、RAG 文档 ChunkID 秒级反查的底层核心思路。
"""

from __future__ import annotations


def two_sum_bruteforce(nums: list[int], target: int) -> list[int]:
    """解法一：双层循环暴力枚举所有组合，最容易想到，但数据量大时性能差。"""
    n = len(nums)
    for i in range(n):
        # j 从 i + 1 开始，避免自己和自己配对，也避免重复检查 (j, i)
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []


def two_sum_hash(nums: list[int], target: int) -> list[int]:
    """解法二：一次遍历哈希表，用 O(n) 空间把时间复杂度从 O(n^2) 降到 O(n)。"""
    seen: dict[int, int] = {}  # key=数值, value=该数值第一次出现时的下标

    for i, num in enumerate(nums):
        need = target - num  # 我们要找的互补搭档
        if need in seen:
            return [seen[need], i]
        # 注意顺序：先查再存！这样可以保证 [3, 3] 目标为 6 时不会自己匹配自己
        seen[num] = i

    return []


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([2, 7, 11, 15], 9, [0, 1]),
        ([3, 2, 4], 6, [1, 2]),
        ([3, 3], 6, [0, 1]),
        ([-3, 4, 3, 90], 0, [0, 2]),
    ]
    for solver in (two_sum_bruteforce, two_sum_hash):
        for nums, target, expected in cases:
            actual = solver(nums, target)
            assert actual == expected, f'{solver.__name__} 失败: 实际={actual}, 期望={expected}'
    print('✅ LeetCode 1 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 1. 两数之和 {'*' * 12}", sep='', end='\n\n')
    nums, target = [2, 7, 11, 15], 9
    print(f'输入: nums={nums}, target={target}')
    print(f'哈希表解法下标结果: {two_sum_hash(nums, target)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
