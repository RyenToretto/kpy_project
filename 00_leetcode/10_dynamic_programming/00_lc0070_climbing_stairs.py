"""
[题目编号]: LeetCode 70. 爬楼梯 (Climbing Stairs)
[难度]: Easy (动态规划第一课：看懂记忆化递归如何演进成 DP)
[所属专题]: 10_dynamic_programming
[前置知识]: 函数递归、functools.lru_cache、for 循环

一、题目描述
假设你正在爬楼梯，需要 `n` 阶才能到达楼顶。
每次你可以爬 `1` 或 `2` 个台阶。请问有多少种不同的方法可以爬到楼顶？

示例:
- 输入: n = 2 -> 输出: 2 (1+1 或 2)
- 输入: n = 3 -> 输出: 3 (1+1+1, 1+2, 2+1)
- 边界: n = 1 -> 1；n = 0 -> 1

二、解法对比与复杂度（三步进阶演示）
1. 解法一（记忆化递归 Top-Down）:
   - 思路: 想站上第 `n` 阶，最后一步要么从 `n-1` 跨 1 阶上来，要么从 `n-2` 跨 2 阶上来，所以 `f(n) = f(n-1) + f(n-2)`。
     加上 `@lru_cache(maxsize=None)` 缓存算过的台阶数，避免指数级重复递归！
   - 时间复杂度: O(n)，空间复杂度: O(n)
2. 解法二（标准一维 DP 数组 Bottom-Up）:
   - 思路: 从 `dp[1]=1, dp[2]=2` 一阶一阶往上算到 `dp[n]`。
   - 时间复杂度: O(n)，空间复杂度: O(n)
3. 解法三（滚动变量状态压缩 - 最优）:
   - 思路: 算当前台阶只用到了「前两阶」，所以根本不需要存整个数组，两个变量 `prev2, prev1` 滚动往前推即可！
   - 时间复杂度: O(n)，空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 从暴力递归到 DP 的通用思维范式: 大模型解码搜索 (Beam Search / Viterbi)、资源调度递推，都是先写出递归转移关系，再加缓存或转成迭代填表。
"""

from __future__ import annotations

from functools import lru_cache


def climb_stairs_memo(n: int) -> int:
    """解法一：记忆化递归，最贴近数学递推直觉。"""
    @lru_cache(maxsize=None)
    def dfs(step: int) -> int:
        if step <= 1:
            return 1
        return dfs(step - 1) + dfs(step - 2)

    return dfs(n)


def climb_stairs_dp(n: int) -> int:
    """解法二：标准一维 dp 数组填表，清晰展示状态定义与转移方程。"""
    if n <= 1:
        return 1

    dp = [0] * (n + 1)
    dp[0] = 1
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def climb_stairs_o1(n: int) -> int:
    """解法三：滚动变量状态压缩，空间复杂度降到 O(1)。"""
    if n <= 1:
        return 1

    prev2, prev1 = 1, 1  # 分别代表 dp[i-2] 和 dp[i-1]
    for _ in range(2, n + 1):
        curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    return prev1


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 3),
        (5, 8),
        (10, 89),
    ]
    for solver in (climb_stairs_memo, climb_stairs_dp, climb_stairs_o1):
        for n, expected in cases:
            assert solver(n) == expected, f'{solver.__name__} 失败: n={n}'
    print('✅ LeetCode 70 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 70. 爬楼梯 {'*' * 12}", sep='', end='\n\n')
    for n in (3, 5, 10):
        print(f'{n} 阶楼梯走法数 = {climb_stairs_o1(n)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
