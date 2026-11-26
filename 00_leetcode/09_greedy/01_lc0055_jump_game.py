"""
[题目编号]: LeetCode 55. 跳跃游戏 (Jump Game)
[难度]: Medium
[所属专题]: 09_greedy
[前置知识]: for 循环、max 函数、列表下标、递归与记忆化（动态规划的入门）

一、题目描述
给定非负整数数组 nums，nums[i] 表示你在位置 i 最多可以向前跳的步数。
起点是下标 0，判断你能否到达最后一个下标。
- 输入: nums = [2, 3, 1, 1, 4] -> True（0 跳 1 步到 1，再跳 3 步到 4）
- 输入: nums = [3, 2, 1, 0, 4] -> False（下标 3 的步数是 0，永远被卡住）
- 边界: nums = [0] -> True（已经在终点）

二、解法对比
1. 解法一（直观版：递归 + 记忆化）:
   - 思路: 从位置 i 出发，依次尝试跳 1 ~ nums[i] 步，只要有一条路能到终点就返回 True。记忆化避免重复计算。
   - 时间复杂度: O(n^2)（每个位置最多尝试 n 个跳跃距离）
   - 空间复杂度: O(n)（记忆化表与递归栈）
2. 解法二（最优版：贪心维护最远可达位置）:
   - 思路: 从左到右扫描，维护“目前能到达的最远下标” reach。如果某个位置 i 已经超过 reach，说明它根本到不了，直接失败；否则更新 reach = max(reach, i + nums[i])。
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- **任务调度 / 资源可达性**: 判断一条流水线的每个阶段是否能被前面的输出“覆盖”，贪心的最远可达思路与之一致。
- **Agent 规划**: 判断目标是否在当前工具与步数限制下可达，可以先用这种“最远可达”做可行性剪枝。
- **网络路由 / 带宽估算**: 在单向链路中判断某节点是否可达，同样是最远覆盖的思路。
"""

from __future__ import annotations

from functools import lru_cache


def solve_bruteforce(nums: list[int]) -> bool:
    """解法一：从起点递归尝试所有跳法，用 lru_cache 记住每个位置的答案，避免重复计算。"""
    last = len(nums) - 1

    @lru_cache(maxsize=None)  # 记忆化：同一个位置只计算一次
    def can_reach(i: int) -> bool:
        if i >= last:  # 已经到达或超过最后一个下标
            return True
        for step in range(1, nums[i] + 1):  # 尝试从 i 跳 1 ~ nums[i] 步
            if can_reach(i + step):
                return True
        return False

    return can_reach(0)


def solve_optimal(nums: list[int]) -> bool:
    """解法二：贪心，维护目前能到达的最远下标 reach。"""
    reach = 0  # 目前能到达的最远下标
    for i, jump in enumerate(nums):  # 从左到右扫描每个位置
        if i > reach:  # 当前位置都到不了，后面更不可能到达
            return False
        reach = max(reach, i + jump)  # 从 i 出发能覆盖的新范围
        if reach >= len(nums) - 1:  # 已经覆盖到最后一个下标，提前返回
            return True
    return True


def run_tests() -> None:
    """自动化断言测试：覆盖可达、不可达、单元素与卡在 0 等边界。"""
    cases = [
        ([2, 3, 1, 1, 4], True),
        ([3, 2, 1, 0, 4], False),
        ([0], True),  # 只有一个元素，本来就在终点
        ([2, 0, 0], True),  # 0 可以跳到 2，正好到达终点
        ([1, 0, 1, 0], False),  # 在下标 1 被卡住
        ([0, 1], False),  # 起点步数为 0，无法移动
    ]
    for solver in (solve_bruteforce, solve_optimal):
        for nums, expected in cases:
            assert solver(nums) == expected, (solver.__name__, nums)
    print('✅ 跳跃游戏所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 55. 跳跃游戏 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例：能否到达最后一个下标
    sample = [2, 3, 1, 1, 4]
    print(f'示例: nums = {sample}，能否到达终点 = {solve_optimal(sample)}')
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
