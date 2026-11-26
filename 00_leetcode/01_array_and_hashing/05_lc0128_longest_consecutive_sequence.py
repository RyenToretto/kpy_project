"""
[题目编号]: LeetCode 128. 最长连续序列 (Longest Consecutive Sequence)
[难度]: Medium (面试高频)
[所属专题]: 01_array_and_hashing
[前置知识]: set 集合去重与 O(1) 查找、while 循环

一、题目描述
给定一个未排序的整数数组 `nums`，找出数字连续的最长序列（不要求序列元素在原数组中连续）的长度。
请你设计并实现时间复杂度为 `O(n)` 的算法解决此问题。

示例:
- 输入: nums = [100, 4, 200, 1, 3, 2]
- 输出: 4  (最长连续序列是 [1, 2, 3, 4]，长度为 4)
- 边界: [] -> 0；[0, 3, 7, 2, 5, 8, 4, 6, 0, 1] -> 9

二、解法对比与复杂度
1. 解法一（排序去重计数 - 好想但 O(n log n)）:
   - 思路: 先排序，遇到相等跳过，遇到 `+1` 就连击计数 `+1`，否则重置为 `1`。
   - 时间复杂度: O(n log n)
   - 空间复杂度: O(n)
2. 解法二（哈希集合 + 只从序列起点触发计数 - O(n) 神级优化）:
   - 思路: 把所有数放入 `num_set` 去重。遍历每个 `num`：
     **关键剪枝**：如果 `num - 1` 也在集合里，说明 `num` 绝对不是连续序列的起点，直接跳过！
     只有当 `num - 1 not in num_set` 时，才说明 `num` 是某个连续段的「老大哥（起点）」，此时用 `while` 一路探测 `num + 1, num + 2, ...` 并统计长度。
     因为每个数最多只会被某一个起点的 `while` 访问一次，整体均摊时间严格 O(n)！
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 时序数据与日志会话分析: 在传感器断电重连检测、用户连续登录天数统计、流数据空洞检测中，往往不能做全量全局排序，用集合找区间起点即可在线性时间完成连续段聚合。
"""

from __future__ import annotations


def longest_consecutive_sort(nums: list[int]) -> int:
    """解法一：排序后线性扫描，逻辑直观但时间复杂度为 O(n log n)。"""
    if not nums:
        return 0

    ordered = sorted(set(nums))  # 去重并排序
    best = 1
    streak = 1

    for i in range(1, len(ordered)):
        if ordered[i] == ordered[i - 1] + 1:
            streak += 1
            best = max(best, streak)
        else:
            streak = 1

    return best


def longest_consecutive_set(nums: list[int]) -> int:
    """解法二：O(n) 哈希集合解法，只在序列起点 (num - 1 不在集合中) 时才向后扩展。"""
    if not nums:
        return 0

    num_set = set(nums)
    best = 0

    for num in num_set:  # 直接遍历去重后的集合，还能避免重复数字反复计算
        if (num - 1) not in num_set:
            current = num
            streak = 1
            while (current + 1) in num_set:
                current += 1
                streak += 1
            if streak > best:
                best = streak

    return best


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([100, 4, 200, 1, 3, 2], 4),
        ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1], 9),
        ([], 0),
        ([42], 1),
        ([1, 2, 0, 1], 3),
    ]
    for solver in (longest_consecutive_sort, longest_consecutive_set):
        for nums, expected in cases:
            actual = solver(nums)
            assert actual == expected, f'{solver.__name__} 失败: nums={nums}, 实际={actual}'
    print('✅ LeetCode 128 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 128. 最长连续序列 {'*' * 12}", sep='', end='\n\n')
    sample = [100, 4, 200, 1, 3, 2]
    print(f'输入: {sample}, 最长连续长度: {longest_consecutive_set(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
