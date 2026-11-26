"""
[题目编号]: LeetCode 40. 组合总和 II (Combination Sum II / 排序剪枝 + 树层去重)
[难度]: Medium (回溯「树层去重 vs 树枝去重」最核心标准模板题，与 LC 39 对比记忆)
[所属专题]: 08_backtracking
[前置知识]: 08_backtracking/01_lc0078_subsets (子集回溯 `start_index`)、排序剪枝

一、题目描述
给定一个候选人编号的集合 `candidates`（**可能包含重复数字**）和一个目标数 `target`，找出 `candidates` 中所有可以使数字和为 `target` 的组合。
规则：
- `candidates` 中的每个数字在每个组合中**只能使用一次**；
- 解集**不能包含重复的组合**（例如 `[1, 7]` 和 `[7, 1]`、或选第一个 `1` 还是第二个 `1` 构成的相同 `[1, 7]` 只能保留一个）。

示例:
- 输入: candidates = [10, 1, 2, 7, 6, 1, 5], target = 8
- 输出: [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
- 输入: candidates = [2, 5, 2, 1, 2], target = 5 -> 输出: [[1, 2, 2], [5]]

与 **LC 39 (组合总和)** 的关键区别：
- LC 39 无重复元素、且同一元素可无限重复选（下层递归传 `i` 而不是 `i + 1`，也不需要树层去重）；
- 本题 **LC 40** 每个下标最多选一次（递归传 `i + 1`），且原数组有重复数，必须做**树层去重**！

二、核心心法（回溯三部曲 + 树层去重 vs 树枝去重）
1. **先排序**：`candidates.sort()`，让相同的数字紧挨在一起，顺便还能做**求和剪枝**（`if remaining < candidates[i]: break`）。
2. **「同一树枝可以重复值，同一树层不能重复值」**：
   - 在 `[1, 1, 6]` 里，两个 `1` 来自不同下标（同一条纵向递归树枝上选了第一个 `1`，下一层选了第二个 `1`），这是**合法的**！
   - 但在**同一层 `for i in range(start, n)`** 里，如果前面刚刚用下标 `start` 试过值为 `1` 的分支，那么同层下一个同样值为 `1` 的下标 `i > start` 再作为当前层起点时，只会搜出完全重复的方案——必须跳过！
   - 浓缩为一行经典条件：`if i > start and candidates[i] == candidates[i - 1]: continue`！

三、解法对比与复杂度
1. 解法一（排序 + `set` 对结果元组去重，容易超时）:
   - 思路: 先枚举所有和为 target 的索引组合，再用 `set(tuple(...))` 事后去重；大量重复元素（如 `[1]*30`）时会做海量无效递归。
2. 解法二（排序 + 剪枝 + 树层去重最优版）:
   - 时间复杂度: 最坏 O(2^n * n)，实际通过剪枝与树层去重快几个数量级
   - 空间复杂度: O(n)（递归栈与路径，不算返回结果）

四、工程与 AI/大数据实战映射
- **多条件预算/资源组合推荐与去重**: 在固定预算 `target` 下组合不同规格的服务包（多个同价套餐项）生成唯一推荐方案，避免向用户重复推荐等价配置。
"""

from __future__ import annotations


def combination_sum2_naive_set(candidates: list[int], target: int) -> list[list[int]]:
    """解法一：排序后直接回溯，再用 set 对结果事后去重（无树层剪枝，仅适合作小数组对拍）。"""
    ordered = sorted(candidates)
    results_set: set[tuple[int, ...]] = set()
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            results_set.add(tuple(path))
            return
        for i in range(start, len(ordered)):
            if ordered[i] > remaining:
                break
            path.append(ordered[i])
            backtrack(i + 1, remaining - ordered[i])
            path.pop()

    backtrack(0, target)
    return [list(item) for item in sorted(results_set)]


def combination_sum2_pruned(candidates: list[int], target: int) -> list[list[int]]:
    """解法二：排序 + 剪枝 + 树层去重 (`i > start and ordered[i] == ordered[i - 1]`)。"""
    ordered = sorted(candidates)
    results: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            results.append(path.copy())  # 必须浅拷贝快照，防止后续 pop 修改已存结果
            return

        for i in range(start, len(ordered)):
            val = ordered[i]
            # 1. 有序剪枝：后面的数只会更大，不可能再凑出 remaining
            if val > remaining:
                break
            # 2. 树层去重：i > start 说明在“同一层”横向换成了第二个相同数值，必会产出重复组合
            if i > start and val == ordered[i - 1]:
                continue

            path.append(val)
            backtrack(i + 1, remaining - val)  # 注意传 i + 1：同一树枝允许用“下一张同面值卡片”
            path.pop()

    backtrack(0, target)
    return results


def run_tests() -> None:
    """自动化断言测试，特别覆盖大量重复元素压测与无解边界。"""
    cases = [
        ([10, 1, 2, 7, 6, 1, 5], 8, [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]),
        ([2, 5, 2, 1, 2], 5, [[1, 2, 2], [5]]),
        ([1, 1, 1], 2, [[1, 1]]),
        ([3, 4], 2, []),
        ([], 5, []),
    ]
    for solver in (combination_sum2_naive_set, combination_sum2_pruned):
        for candidates, target, expected in cases:
            actual = solver(candidates, target)
            assert actual == expected, f'{solver.__name__} 失败: {candidates}, target={target} -> {actual}'

    # 大量重复数字压测：树层去重能在毫秒级得出结果（若没有树层去重会跑 2^25 次递归卡死）
    many_ones = [1] * 25
    assert combination_sum2_pruned(many_ones, 3) == [[1, 1, 1]]
    print('✅ LeetCode 40 (组合总和 II / 树层去重) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 40. 组合总和 II (树层去重) {'*' * 12}", sep='', end='\n\n')
    sample = [10, 1, 2, 7, 6, 1, 5]
    print(f'候选集: {sample}, target=8 -> 唯一组合: {combination_sum2_pruned(sample, 8)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
