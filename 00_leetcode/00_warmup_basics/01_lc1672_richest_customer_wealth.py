"""
[题目编号]: LeetCode 1672. 最富有客户的资产总量 (Richest Customer Wealth)
[难度]: Easy
[所属专题]: 00_warmup_basics
[前置知识]: 嵌套列表 (二维数组)、for 循环、内置函数 sum() / max()

一、题目描述
给你一个 m x n 的二维整数网格 `accounts`，其中 `accounts[i][j]` 表示第 `i` 位客户在第 `j` 家银行托管的资产数量。
返回最富有客户所拥有的「资产总量」（即每一行求和后的最大值）。

示例:
- 输入: accounts = [[1, 2, 3], [3, 2, 1]]
- 输出: 6  (第 0 位和第 1 位客户资产都是 6)
- 边界: 只有一个客户 [[7]] -> 7；某客户全为 0 [[0, 0], [5, 1]] -> 6

二、解法对比与复杂度
1. 解法一（新手双层循环版）:
   - 思路: 外层循环遍历每位客户，内层循环把该客户所有银行账户加起来，再手动更新最大值 `best`。
   - 时间复杂度: O(m * n)，每个元素访问一次。
   - 空间复杂度: O(1)，只用了几个标量变量。
2. 解法二（Python 生成器表达式版）:
   - 思路: `max((sum(row) for row in accounts), default=0)`，一行表达「按行聚合求最大」。
   - 时间复杂度: O(m * n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 数据分析: 类似 Pandas / SQL 中的「按用户分组求和后再取 Top-1 (`groupby('user_id')['amount'].sum().max()`)」。
- 向量计算: 二维列表就是未来学习 NumPy 矩阵 (`axis=1` 按行聚合) 的最直观原型。
"""

from __future__ import annotations


def maximum_wealth_basic(accounts: list[list[int]]) -> int:
    """解法一：双层循环手动求和与比较，适合小白理解二维列表遍历。"""
    if not accounts:
        return 0

    best = 0  # 记录目前见过的最大资产总量
    for customer_accounts in accounts:
        current_total = 0  # 每次切换新客户时，累计值要清零
        for money in customer_accounts:
            current_total += money
        if current_total > best:
            best = current_total

    return best


def maximum_wealth_pythonic(accounts: list[list[int]]) -> int:
    """解法二：Pythonic 写法，借助内置 sum() 与 max() 完成行聚合。"""
    return max((sum(row) for row in accounts), default=0)


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([[1, 2, 3], [3, 2, 1]], 6),
        ([[1, 5], [7, 3], [3, 5]], 10),
        ([[2, 8, 7], [7, 1, 3], [1, 9, 5]], 17),
        ([[7]], 7),
        ([[0, 0], [5, 1]], 6),
        ([], 0),
    ]
    for solver in (maximum_wealth_basic, maximum_wealth_pythonic):
        for accounts, expected in cases:
            actual = solver(accounts)
            assert actual == expected, f'{solver.__name__} 失败: 实际={actual}, 期望={expected}'
    print('✅ LeetCode 1672 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 1672. 最富有客户的资产总量 {'*' * 12}", sep='', end='\n\n')
    sample = [[1, 5], [7, 3], [3, 5]]
    print(f'客户资产矩阵: {sample}')
    print(f'最富有客户的资产总量: {maximum_wealth_pythonic(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
