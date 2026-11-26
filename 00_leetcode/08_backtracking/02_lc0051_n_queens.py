"""
[题目编号]: LeetCode 51. N 皇后 (N-Queens)
[难度]: Hard
[所属专题]: 08_backtracking
[前置知识]: 01_lc0078_subsets (回溯的撤销选择)、set 集合、列表推导式、itertools.permutations

一、题目描述
n 皇后问题：在 n × n 的棋盘上放置 n 个皇后，使它们互不攻击（任意两个皇后不在同一行、同一列、同一条斜线上）。
返回所有不同的解，每个解是一个棋盘表示：'Q' 表示皇后，'.' 表示空位。
- 输入: n = 4 -> 输出 2 个解
- 输入: n = 1 -> 输出 [["Q"]]
- 常见结果: n = 8 时共 92 个解

二、解法对比
1. 解法一（直观版：枚举所有排列再检查）:
   - 思路: 每个皇后占一列，用 permutations 枚举所有“行号排列”，逐个检查是否有斜线冲突。
   - 时间复杂度: O(n! × n^2)（排列数 n! 很大，只适合 n 很小时）
   - 空间复杂度: O(n)
2. 解法二（最优版：按行回溯 + 集合剪枝）:
   - 思路: 一行一行放皇后。用三个集合记录已经被占用的列、主对角线（row - col）、副对角线（row + col）。
     冲突的位置直接跳过，不再继续往下搜，这就是“剪枝”。放完一行后递归到下一行，再撤销。
   - 时间复杂度: 最坏 O(n!)，但剪枝后远小于此；集合判断为 O(1)
   - 空间复杂度: O(n)（三个集合与递归栈）

三、工程与 AI/大数据实战映射
- **约束求解 / 排班与资源分配**: 每个资源只能被占用一次（行/列约束），与 N 皇后的“互不冲突”是同一类问题，常用回溯 + 剪枝求解。
- **Agent 规划**: 多步动作之间存在互斥约束时，回溯可以在早期发现死路并回退，避免无效搜索。
- **数据库与调度**: 时间冲突检测（同一资源不能在同一时段使用）可以用“行/列/斜线”集合的思想加速。
"""

from __future__ import annotations

from itertools import permutations


def solve_bruteforce(n: int) -> list[list[str]]:
    """解法一：枚举 0 ~ n-1 的所有排列作为每列皇后所在的行，检查两两是否在同一斜线上。"""
    results: list[list[str]] = []
    for perm in permutations(range(n)):  # perm[col] = row，表示第 col 列的皇后放在第 row 行
        # 检查任意两个皇后的斜线冲突：行差等于列差即为同一条斜线
        conflict = any(
            abs(perm[i] - perm[j]) == j - i
            for i in range(n)
            for j in range(i + 1, n)
        )
        if not conflict:
            results.append(['.' * col + 'Q' + '.' * (n - col - 1) for col in perm])  # 拼成棋盘字符串
    return results


def solve_optimal(n: int) -> list[list[str]]:
    """解法二：按行回溯，用集合记录被占用的列与两条斜线，冲突位置直接跳过。"""
    results: list[list[str]] = []
    cols: set[int] = set()  # 已占用的列
    diag_main: set[int] = set()  # 已占用的主对角线：row - col 相同
    diag_anti: set[int] = set()  # 已占用的副对角线：row + col 相同
    placement: list[int] = []  # placement[row] = col

    def backtrack(row: int) -> None:
        if row == n:  # 所有行都放好了，记录一个解
            results.append(['.' * c + 'Q' + '.' * (n - c - 1) for c in placement])
            return
        for col in range(n):  # 尝试当前行的每一列
            if col in cols or (row - col) in diag_main or (row + col) in diag_anti:
                continue  # 剪枝：这个位置会被攻击，跳过
            cols.add(col)  # 做选择
            diag_main.add(row - col)
            diag_anti.add(row + col)
            placement.append(col)
            backtrack(row + 1)  # 进入下一行
            placement.pop()  # 撤销选择
            cols.remove(col)
            diag_main.remove(row - col)
            diag_anti.remove(row + col)

    backtrack(0)
    return results


def run_tests() -> None:
    """自动化断言测试：覆盖 n=1、n=4、n=6 与 n=8 的解数，并校验两种解法结果一致。"""
    assert solve_optimal(1) == [['Q']]
    assert solve_bruteforce(1) == [['Q']]

    # n = 4 有 2 个解；两种解法结果一致（排序后比较）
    assert len(solve_optimal(4)) == 2
    assert sorted(solve_bruteforce(4)) == sorted(solve_optimal(4))

    # n = 6 有 4 个解
    assert len(solve_optimal(6)) == 4
    assert sorted(solve_bruteforce(6)) == sorted(solve_optimal(6))

    # 经典结果：n = 8 有 92 个解（只跑回溯版，暴力版太慢）
    assert len(solve_optimal(8)) == 92

    # 每个解都必须恰好有 n 个皇后，且每行每列只有一个
    for board in solve_optimal(8):
        assert sum(row.count('Q') for row in board) == 8
        assert all(row.count('Q') == 1 for row in board)

    print('✅ N 皇后所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 51. N 皇后 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例：n = 4 的第一个解
    solutions = solve_optimal(4)
    print(f'n = 4 共有 {len(solutions)} 个解，第一个解:')
    for row in solutions[0]:
        print(row)
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
