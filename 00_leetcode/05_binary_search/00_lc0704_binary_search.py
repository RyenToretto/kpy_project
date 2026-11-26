"""
[题目编号]: LeetCode 704. 二分查找 (Binary Search)
[难度]: Easy
[所属专题]: 05_binary_search
[前置知识]: while 循环、`//` 整除、bisect 标准库

一、题目描述
给定一个升序排列的整型数组 `nums` 和一个目标值 `target`，写一个函数搜索 `nums` 中的 `target`：
如果目标值存在返回下标，否则返回 `-1`。要求时间复杂度为 `O(log n)`。

示例:
- 输入: nums = [-1, 0, 3, 5, 9, 12], target = 9 -> 输出: 4
- 输入: nums = [-1, 0, 3, 5, 9, 12], target = 2 -> 输出: -1
- 边界: [] -> -1；[5], target=5 -> 0；[5], target=1 -> -1

二、解法对比与复杂度
1. 解法一（手写左闭右闭 `[left, right]` 区间二分 - 面试必背）:
   - 思路: 因为 `left` 和 `right` 都是有效下标，当 `left == right` 时区间依然有 1 个合法元素需要检查，所以循环条件是 `while left <= right`。
   - 时间复杂度: O(log n)
   - 空间复杂度: O(1)
2. 解法二（Python 标准库 bisect_left 工程版）:
   - 思路: 实际开发中尽量复用 C 实现的 `bisect.bisect_left`，找到第一个 `>= target` 的位置再校验是否越界与相等。

三、工程与 AI/大数据实战映射
- 检索与底层索引: B+ 树页内二分、大模型推理中的累积概率采样（`searchsorted` / `bisect`）、日志时间戳区间定位全靠二分查找。
"""

from __future__ import annotations

from bisect import bisect_left


def binary_search_manual(nums: list[int], target: int) -> int:
    """解法一：标准左闭右闭 [left, right] 二分查找模板。"""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2  # 通用防溢出写法（在其他语言里很关键）
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            left = mid + 1  # mid 已经检查过且偏小，从 mid+1 开始找右半边
        else:
            right = mid - 1  # mid 偏大，缩小到 mid-1

    return -1


def binary_search_bisect(nums: list[int], target: int) -> int:
    """解法二：Python 标准库 bisect_left 工程用法。"""
    idx = bisect_left(nums, target)
    if idx < len(nums) and nums[idx] == target:
        return idx
    return -1


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([-1, 0, 3, 5, 9, 12], 9, 4),
        ([-1, 0, 3, 5, 9, 12], 2, -1),
        ([5], 5, 0),
        ([5], 1, -1),
        ([], 3, -1),
    ]
    for solver in (binary_search_manual, binary_search_bisect):
        for nums, target, expected in cases:
            assert solver(nums, target) == expected, f'{solver.__name__} 失败: {nums}, {target}'
    print('✅ LeetCode 704 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 704. 二分查找 {'*' * 12}", sep='', end='\n\n')
    nums = [-1, 0, 3, 5, 9, 12]
    print(f'数组 {nums} 中查找 9 的下标: {binary_search_manual(nums, 9)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
