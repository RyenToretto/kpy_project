"""
[题目编号]: LeetCode 46. 全排列 (Permutations)
[难度]: Medium (回溯算法第一标准模板题)
[所属专题]: 08_backtracking
[前置知识]: 递归、列表浅拷贝 `.copy()`、状态恢复 (Pop)

一、题目描述
给定一个不含重复数字的数组 `nums`，返回其所有可能的全排列，可以按任意顺序返回。

示例:
- 输入: nums = [1, 2, 3]
- 输出: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
- 边界: [1] -> [[1]]；[] -> [[]]

二、解法与复杂度
- 核心思路（回溯三步曲：做选择 -> 递归 -> 撤销选择）:
  1. 用 `path` 记录当前已经选了哪些数字，`used[i]` 记录下标 `i` 是否已经在 `path` 里。
  2. **新手最常踩的大坑**：收集答案时必须写 `result.append(path.copy())`，绝对不能写 `result.append(path)`！
     因为 Python 列表是引用类型，如果直接 append `path`，后面撤销选择 `path.pop()` 会把刚才放进 `result` 的内容一起清空！
- 时间复杂度: O(n * n!)，共 n! 个排列，每次拷贝耗时 O(n)。
- 空间复杂度: O(n)（递归深度与 `used` 数组，不计结果集）。

三、工程与 AI/大数据实战映射
- AI Agent 规划与超参搜索: 当 Agent 尝试多步工具调用路径或做动作树搜索遇到死路需要**回退状态 (Rollback)** 时，核心框架就是回溯搜索。
"""

from __future__ import annotations


def permute(nums: list[int]) -> list[list[int]]:
    """经典回溯模板实现全排列。"""
    result: list[list[int]] = []
    path: list[int] = []
    used = [False] * len(nums)

    def backtrack() -> None:
        # 终止条件：当前路径长度已经凑够所有数字
        if len(path) == len(nums):
            result.append(path.copy())  # 务必 .copy()，拍下当前列表快照！
            return

        for i, num in enumerate(nums):
            if used[i]:
                continue
            # 1. 做选择
            used[i] = True
            path.append(num)
            # 2. 进入下一层决策树
            backtrack()
            # 3. 撤销选择（恢复现场，让同层循环尝试下一个数字）
            path.pop()
            used[i] = False

    backtrack()
    return result


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([1, 2, 3], [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
        ([0, 1], [[0, 1], [1, 0]]),
        ([1], [[1]]),
        ([], [[]]),
    ]
    for nums, expected in cases:
        actual = permute(nums)
        assert sorted(actual) == sorted(expected), f'失败: nums={nums}, 实际={actual}'
    print('✅ LeetCode 46 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 46. 全排列 {'*' * 12}", sep='', end='\n\n')
    sample = [1, 2, 3]
    print(f'{sample} 的全排列: {permute(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
