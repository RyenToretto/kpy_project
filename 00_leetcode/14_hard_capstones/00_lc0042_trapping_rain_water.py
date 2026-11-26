"""
[题目编号]: LeetCode 42. 接雨水 (Trapping Rain Water)
[难度]: Hard (字节/阿里/腾讯面试最爱考察的综合 Hard 题)
[所属专题]: 14_hard_capstones
[前置知识]: 02_two_pointers、04_stack_and_queue 单调栈

一、题目描述
给定 `n` 个非负整数表示每个宽度为 `1` 的柱子的高度图，计算按此排列的柱子下雨之后能接多少雨水。

示例:
- 输入: height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1] -> 输出: 6
- 输入: height = [4, 2, 0, 3, 2, 5] -> 输出: 9
- 边界: 长度 < 3 -> 0；单调递增或递减 -> 0

二、解法对比与复杂度
核心物理规律：第 `i` 根柱子头顶能装多少水，取决于它「左边最高柱子」和「右边最高柱子」里较矮的那一块短板：
`water[i] = max(0, min(left_max[i], right_max[i]) - height[i])`

1. 解法一（双指针木桶短板原理 - O(n) 时间 + O(1) 空间最优）:
   - 思路: `left=0, right=n-1`，同时记录 `left_max` 和 `right_max`。
     如果 `left_max < right_max`，说明对于左指针 `left` 来说，它左边的短板 `left_max` 已经比右边的某根高墙 `right_max` 还要矮了——不管中间还有没有更高的柱子，决定 `left` 位置水位的短板一定就是 `left_max`！于是直接结算 `left` 并右移。反之结算 `right`。
   - 时间复杂度: O(n)，空间复杂度: O(1)
2. 解法二（单调递减栈按「行」横向积水 - 锻炼单调栈极限功底）:
   - 思路: 遇到比栈顶更高的柱子时，说明形成了一个凹槽！弹出槽底 `bottom`，左墙是新栈顶 `stack[-1]`，右墙是当前 `i`，积水高 = `min(左墙, 右墙) - 槽底`，宽 = `i - stack[-1] - 1`。
   - 时间复杂度: O(n)，空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 时序波形分析 / 地形蓄水与峰值凹槽计算: 在工业传感器谷值容量、音频波形包络差估算中，双指针单遍 O(1) 空间扫描非常优雅。
"""

from __future__ import annotations


def trap_two_pointers(height: list[int]) -> int:
    """解法一：相向双指针，按列算水，时空最优 (O(n), O(1))。"""
    if len(height) < 3:
        return 0

    left, right = 0, len(height) - 1
    left_max, right_max = 0, 0
    water = 0

    while left < right:
        left_max = max(left_max, height[left])
        right_max = max(right_max, height[right])

        if left_max < right_max:
            # 左边最大值已经是确定的短板，直接结算 left 这一列的水量
            water += left_max - height[left]
            left += 1
        else:
            water += right_max - height[right]
            right -= 1

    return water


def trap_monotonic_stack(height: list[int]) -> int:
    """解法二：单调递减栈，按水平层横向累加雨水。"""
    stack: list[int] = []
    water = 0

    for i, h in enumerate(height):
        while stack and h > height[stack[-1]]:
            bottom_idx = stack.pop()
            if not stack:
                break  # 左边没有墙了，接不住水
            left_wall_idx = stack[-1]
            bounded_height = min(height[left_wall_idx], h) - height[bottom_idx]
            width = i - left_wall_idx - 1
            water += bounded_height * width
        stack.append(i)

    return water


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
        ([4, 2, 0, 3, 2, 5], 9),
        ([1, 2, 3, 4], 0),
        ([4, 2], 0),
        ([], 0),
    ]
    for solver in (trap_two_pointers, trap_monotonic_stack):
        for height, expected in cases:
            assert solver(height) == expected, f'{solver.__name__} 失败: {height}'
    print('✅ LeetCode 42 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 42. 接雨水 (Hard) {'*' * 12}", sep='', end='\n\n')
    sample = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
    print(f'柱子高度: {sample}')
    print(f'总接雨水量: {trap_two_pointers(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
