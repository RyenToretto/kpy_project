"""
[题目编号]: LeetCode 45. 跳跃游戏 II (Jump Game II)
[难度]: Medium (在 LC 55 可达性之上求最少跳跃次数)
[所属专题]: 09_greedy
[前置知识]: 09_greedy/01_lc0055_jump_game

一、题目描述
给定一个长度为 n 的 0 索引整数数组 `nums`。初始位置为 nums[0]。
每个元素 `nums[i]` 表示从索引 i 向前跳的最大长度。假设你总是可以到达数组的最后一个索引，返回到达终点的最小跳跃次数。

示例:
- [2, 3, 1, 1, 4] -> 2 (先跳 1 步到下标 1，再跳 3 步到终点)
- [2, 3, 0, 1, 4] -> 2

二、解法
贪心分层: 维护「当前这一跳能覆盖的最右边界 `end`」和「下一跳能覆盖的最远 `farthest`」。
遍历到 `end` 时必须再跳一次，`steps += 1`，并把 `end` 更新为 `farthest`。
时间 O(n)，空间 O(1)。

三、工程映射
- 最少中转次数: CDN 跳数、消息队列最少转发层数（每层覆盖范围已知）。
"""

from __future__ import annotations


def jump(nums: list[int]) -> int:
    """贪心分层求最少跳跃次数。"""
    steps = 0
    end = 0
    farthest = 0
    # 最后一格不需要再跳，所以只遍历到 n-2
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == end:
            steps += 1
            end = farthest
    return steps


def run_tests() -> None:
    assert jump([2, 3, 1, 1, 4]) == 2
    assert jump([2, 3, 0, 1, 4]) == 2
    assert jump([1]) == 0
    assert jump([1, 2]) == 1
    assert jump([1, 1, 1, 1]) == 3
    print('✅ LeetCode 45 (跳跃游戏 II) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 45. 跳跃游戏 II {'*' * 12}", sep='', end='\n\n')
    print(jump([2, 3, 1, 1, 4]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
