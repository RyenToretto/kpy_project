"""
[题目编号]: LeetCode 503. 下一个更大元素 II (Next Greater Element II)
[难度]: Medium (环形数组上的单调栈)
[所属专题]: 04_stack_and_queue
[前置知识]: 04_stack_and_queue/01_lc0739_daily_temperatures

一、题目描述
给定一个循环数组 `nums`（最后一个元素的下一个元素是数组的第一个元素），返回每个元素「下一个更大元素」。
数字 x 的下一个更大元素是指：按数组遍历顺序，这个数字之后的第一个比它更大的数；如果不存在，输出 -1。

示例:
- 输入: [1, 2, 1] -> [2, -1, 2]
- 输入: [1, 2, 3, 4, 3] -> [2, 3, 4, -1, 4]

二、解法
环形处理技巧：把下标空间想象成走两圈，循环 `for i in range(2 * n)`，真实下标取 `i % n`。
用单调递减栈存「还没找到更大值」的下标；遇到更大值就结算。第二圈只负责帮第一圈收尾，不再写入新的待结算下标（或写了也没关系，因为答案数组只在第一次填入时更新）。

- 时间 O(n)，空间 O(n)

三、工程映射
- 环形缓冲/轮询调度: 环形队列里找「下一个更高优先级任务」；周环时序中找下一峰值。
"""

from __future__ import annotations


def next_greater_elements(nums: list[int]) -> list[int]:
    """环形单调递减栈：虚拟走两圈，下标取模。"""
    n = len(nums)
    answer = [-1] * n
    stack: list[int] = []  # 存下标，对应值递减

    for i in range(2 * n):
        idx = i % n
        while stack and nums[idx] > nums[stack[-1]]:
            prev = stack.pop()
            answer[prev] = nums[idx]
        # 第一圈才把下标入栈；第二圈只负责帮前面结算
        if i < n:
            stack.append(idx)
    return answer


def next_greater_bruteforce(nums: list[int]) -> list[int]:
    """暴力：每个位置向后最多看 n-1 步（环形）。"""
    n = len(nums)
    answer = [-1] * n
    for i in range(n):
        for step in range(1, n):
            j = (i + step) % n
            if nums[j] > nums[i]:
                answer[i] = nums[j]
                break
    return answer


def run_tests() -> None:
    cases = [
        ([1, 2, 1], [2, -1, 2]),
        ([1, 2, 3, 4, 3], [2, 3, 4, -1, 4]),
        ([5, 4, 3, 2, 1], [-1, 5, 5, 5, 5]),
        ([1], [-1]),
        ([], []),
    ]
    for solver in (next_greater_bruteforce, next_greater_elements):
        for nums, expected in cases:
            assert solver(nums) == expected, f'{solver.__name__} 失败: {nums}'
    print('✅ LeetCode 503 (环形下一个更大元素) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 503. 下一个更大元素 II {'*' * 12}", sep='', end='\n\n')
    print(next_greater_elements([1, 2, 1]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
