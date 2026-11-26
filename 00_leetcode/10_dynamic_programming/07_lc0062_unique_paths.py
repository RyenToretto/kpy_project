"""
[题目编号]: LeetCode 62. 不同路径 (Unique Paths)
[难度]: Medium (网格路径计数二维 DP 入门)
[所属专题]: 10_dynamic_programming
[前置知识]: 二维列表、10_dynamic_programming/00_lc0070

一、题目描述
一个机器人位于 `m x n` 网格的左上角，只能每次向下或向右移动一步。问到达右下角有多少条不同路径？

示例:
- m=3, n=7 -> 28
- m=3, n=2 -> 3
- m=1, n=1 -> 1

二、解法
`dp[i][j] = dp[i-1][j] + dp[i][j-1]`；第一行/第一列只有 1 种走法。
可压成一维：`dp[j] += dp[j-1]`。
时间 O(m*n)，空间 O(n)。

三、工程映射
- 网格路径计数 / 组合数: 编排中「只能右/下」的步骤方案数；数学上等价于 C(m+n-2, m-1)。
"""

from __future__ import annotations


def unique_paths(m: int, n: int) -> int:
    """一维滚动 DP：逐行更新。"""
    dp = [1] * n  # 第一行全是 1
    for _ in range(1, m):
        for col in range(1, n):
            dp[col] += dp[col - 1]  # 上方旧值 + 左方新值
    return dp[-1]


def unique_paths_2d(m: int, n: int) -> int:
    """二维 DP 直观版。"""
    dp = [[1] * n for _ in range(m)]
    for row in range(1, m):
        for col in range(1, n):
            dp[row][col] = dp[row - 1][col] + dp[row][col - 1]
    return dp[-1][-1]


def run_tests() -> None:
    cases = [(3, 7, 28), (3, 2, 3), (1, 1, 1), (1, 10, 1), (7, 3, 28)]
    for solver in (unique_paths, unique_paths_2d):
        for m, n, expected in cases:
            assert solver(m, n) == expected, f'{solver.__name__} 失败: {m}x{n}'
    print('✅ LeetCode 62 (不同路径) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 62. 不同路径 {'*' * 12}", sep='', end='\n\n')
    print(unique_paths(3, 7))
    run_tests()


if __name__ == '__main__':
    bootstrap()
