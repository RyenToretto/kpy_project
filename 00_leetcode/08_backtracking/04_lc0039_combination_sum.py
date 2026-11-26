"""
[题目编号]: LeetCode 39. 组合总和 (Combination Sum)
[难度]: Medium (可重复选的回溯；与 LC 40 对照)
[所属专题]: 08_backtracking
[前置知识]: 08_backtracking/03_lc0040_combination_sum_ii

一、题目描述
给你一个无重复元素的整数数组 `candidates` 和一个目标整数 `target`，找出 `candidates` 中可以使数字和为目标数 `target` 的所有不同组合。
`candidates` 中的同一个数字可以无限制重复被选取。

示例:
- candidates = [2, 3, 6, 7], target = 7 -> [[2, 2, 3], [7]]
- candidates = [2, 3, 5], target = 8 -> [[2, 2, 2, 2], [2, 3, 3], [3, 5]]

与 LC 40 的关键区别:
- 本题元素无重复、可无限次使用 -> 递归传 `i`（不是 `i+1`），无需树层去重。
- LC 40 每个下标最多一次、原数组有重复 -> 传 `i+1` + 树层去重。

二、复杂度
最坏指数级；排序后可用 `if candidates[i] > remaining: break` 剪枝。

三、工程映射
- 可重复配置组合: 固定预算下可重复选用同一规格资源包生成方案列表。
"""

from __future__ import annotations


def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """可重复选的组合回溯：递归传同一个 i，允许继续用当前数字。"""
    ordered = sorted(candidates)
    results: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            results.append(path.copy())
            return
        for i in range(start, len(ordered)):
            val = ordered[i]
            if val > remaining:
                break
            path.append(val)
            backtrack(i, remaining - val)  # 传 i：同一数字可再用
            path.pop()

    backtrack(0, target)
    return results


def run_tests() -> None:
    assert combination_sum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert combination_sum([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
    assert combination_sum([2], 1) == []
    assert combination_sum([1], 1) == [[1]]
    print('✅ LeetCode 39 (组合总和 / 可重复选) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 39. 组合总和 {'*' * 12}", sep='', end='\n\n')
    print(combination_sum([2, 3, 6, 7], 7))
    run_tests()


if __name__ == '__main__':
    bootstrap()
