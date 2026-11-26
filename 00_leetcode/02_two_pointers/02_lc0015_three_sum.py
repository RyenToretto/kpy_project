"""
[题目编号]: LeetCode 15. 三数之和 (3Sum)
[难度]: Medium (大厂面试必考)
[所属专题]: 02_two_pointers
[前置知识]: 排序 sort()、左右双指针、去重逻辑

一、题目描述
给你一个整数数组 `nums`，判断是否存在三元组 `[nums[i], nums[j], nums[k]]` 满足 `i != j != k` 且 `nums[i] + nums[j] + nums[k] == 0`。
请你返回所有**和为 0 且不重复**的三元组。

示例:
- 输入: nums = [-1, 0, 1, 2, -1, -4]
- 输出: [[-1, -1, 2], [-1, 0, 1]]
- 边界: [0, 1, 1] -> []；[0, 0, 0, 0] -> [[0, 0, 0]]；长度 < 3 -> []

二、解法对比与复杂度
1. 解法（排序 + 固定第一个数 + 左右双指针夹逼）:
   - 为什么先排序？
     1) 排序后相同数字挨在一起，极大简化「结果去重」！
     2) 有序后，三数之和偏大就右指针左移 `right -= 1`，偏小就左指针右移 `left += 1`，把原本需要再套两层的查找变成一次 O(n) 扫描。
   - 剪枝优化: 如果排序后当前最小数 `nums[i] > 0`，后面全比它大，三数之和不可能为 0，直接 `break`！
   - 时间复杂度: O(n^2)（外层循环 O(n) * 内层双指针 O(n)，排序 O(n log n) 被吸收）
   - 空间复杂度: O(1) ~ O(n)（取决于排序与输出列表）

三、工程与 AI/大数据实战映射
- 多维检索与特征组合剪枝: 当面临 O(n^3) 级别多因子组合筛选时，先排序再做单调性双指针剪枝，能瞬间把耗时从不可用降到毫秒级。
"""

from __future__ import annotations


def three_sum(nums: list[int]) -> list[list[int]]:
    """排序 + 固定首位 + 左右双指针（带三重去重与单调剪枝）。"""
    ordered = sorted(nums)
    n = len(ordered)
    result: list[list[int]] = []

    for i in range(n - 2):
        # 剪枝：有序数组中最小数都大于 0 了，后面不可能凑出 0
        if ordered[i] > 0:
            break

        # 去重 1：跳过重复的第一个数（注意是跟前一个 i-1 比，不是 i+1，否则会漏掉 [-1, -1, 2]）
        if i > 0 and ordered[i] == ordered[i - 1]:
            continue

        left, right = i + 1, n - 1
        while left < right:
            total = ordered[i] + ordered[left] + ordered[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([ordered[i], ordered[left], ordered[right]])
                # 去重 2 & 3：找到一组答案后，左右指针同时跳过相同的相邻元素
                while left < right and ordered[left] == ordered[left + 1]:
                    left += 1
                while left < right and ordered[right] == ordered[right - 1]:
                    right -= 1
                left += 1
                right -= 1

    return result


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([-1, 0, 1, 2, -1, -4], [[-1, -1, 2], [-1, 0, 1]]),
        ([0, 1, 1], []),
        ([0, 0, 0], [[0, 0, 0]]),
        ([0, 0, 0, 0], [[0, 0, 0]]),
        ([1, 2], []),
    ]
    for nums, expected in cases:
        actual = three_sum(nums)
        assert actual == expected, f'失败: nums={nums}, 实际={actual}, 期望={expected}'
    print('✅ LeetCode 15 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 15. 三数之和 {'*' * 12}", sep='', end='\n\n')
    sample = [-1, 0, 1, 2, -1, -4]
    print(f'输入: {sample}')
    print(f'去重三元组: {three_sum(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
