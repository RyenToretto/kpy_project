"""
[题目编号]: LeetCode 78. 子集 (Subsets)
[难度]: Medium
[所属专题]: 08_backtracking
[前置知识]: 递归函数、列表 append 与 pop、for 循环、位运算 & 与 <<（解法一用到）

一、题目描述
给定一个由不同整数组成的数组 nums，返回它所有可能的子集（幂集）。解集不能包含重复子集，顺序任意。
- 输入: nums = [1, 2, 3] -> 输出 8 个子集: [], [1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]
- 输入: nums = [0] -> 输出 [], [0]
- 规律: 长度为 n 的数组有 2^n 个子集，每个元素“选”或“不选”。

二、解法对比
1. 解法一（直观版：位掩码枚举）:
   - 思路: 用 0 ~ 2^n - 1 的整数表示每种选择方案，第 i 位为 1 表示选中 nums[i]。
   - 时间复杂度: O(n × 2^n)（2^n 种方案，每种要检查 n 位）
   - 空间复杂度: O(n × 2^n)（输出本身的大小）
2. 解法二（最优版：回溯 + 起始下标）:
   - 思路: 从 start 位置开始，每一步把当前路径记入答案，然后依次尝试把 nums[i]（i ≥ start）加入路径，递归后再撤销（回溯）。
     起始下标 start 保证只向后选，因此不会产生重复子集。
   - 时间复杂度: O(n × 2^n)
   - 空间复杂度: O(n)（不算输出时，递归栈深度为 n）

三、工程与 AI/大数据实战映射
- **组合配置搜索**: A/B 测试里“同时开启哪些功能开关”的所有组合，就是子集枚举；全量枚举前先用回溯剪枝。
- **特征组合 / 特征选择**: 建模时枚举特征子集评估效果，本质是子集问题，需要控制爆炸式增长。
- **Agent 工具组合**: 规划时考虑“哪些工具组合可用”，同样是子集搜索，常用回溯做可行性检查。
"""

from __future__ import annotations


def solve_bruteforce(nums: list[int]) -> list[list[int]]:
    """解法一：枚举 0 ~ 2^n-1 的所有位掩码，第 i 位为 1 就选中 nums[i]。"""
    n = len(nums)
    result: list[list[int]] = []
    for mask in range(1 << n):  # 1 << n 等于 2^n
        subset = []
        for i in range(n):
            if mask & (1 << i):  # 检查第 i 位是否为 1
                subset.append(nums[i])
        result.append(subset)
    return result


def solve_optimal(nums: list[int]) -> list[list[int]]:
    """解法二：回溯。每个路径都是一个合法子集，start 保证只向后选，避免重复。"""
    result: list[list[int]] = []
    path: list[int] = []

    def backtrack(start: int) -> None:
        result.append(path[:])  # 记录当前路径（复制一份，避免之后被修改）
        for i in range(start, len(nums)):  # 只能选择下标 >= start 的元素
            path.append(nums[i])  # 做选择
            backtrack(i + 1)  # 继续向后递归
            path.pop()  # 撤销选择，回到上一层状态

    backtrack(0)
    return result


def _normalize(subsets: list[list[int]]) -> list[tuple[int, ...]]:
    """测试辅助：子集内部与外部的顺序都不重要，统一排序后再比较。"""
    return sorted(tuple(sorted(s)) for s in subsets)


def run_tests() -> None:
    """自动化断言测试：覆盖三元素、单元素、空数组与数量校验。"""
    cases = [
        [1, 2, 3],
        [0],
        [],  # 边界：空数组只有一个空子集
        [4, 5],
    ]
    for nums in cases:
        brute = solve_bruteforce(nums)
        optimal = solve_optimal(nums)
        assert len(optimal) == 2 ** len(nums), nums  # 数量必须是 2^n
        assert _normalize(brute) == _normalize(optimal), nums  # 两种解法结果一致
    assert _normalize(solve_optimal([1, 2, 3])) == _normalize(
        [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    )
    print('✅ 子集所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 78. 子集 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例
    sample = [1, 2, 3]
    print(f'示例: nums = {sample}，子集个数 = {len(solve_optimal(sample))}')
    print('所有子集:', solve_optimal(sample))
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
