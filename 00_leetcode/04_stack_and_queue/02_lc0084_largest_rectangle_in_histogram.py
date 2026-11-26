"""
[题目编号]: LeetCode 84. 柱状图中最大的矩形 (Largest Rectangle in Histogram)
[难度]: Hard (单调递增栈压轴经典题，与 LC 42 接雨水对称双壁)
[所属专题]: 04_stack_and_queue
[前置知识]: 04_stack_and_queue/01_lc0739_daily_temperatures (单调栈)、14_hard_capstones/00_lc0042_trapping_rain_water

一、题目描述
给定 `n` 个非负整数，用来表示柱状图中各个柱子的高度。每个柱子彼此相邻，且宽度为 `1`。
求在该柱状图中，能够勾勒出来的矩形的最大面积。

示例:
- 输入: heights = [2, 1, 5, 6, 2, 3] -> 输出: 10 (高度为 5 和 6 的两根柱子组成 5 * 2 = 10)
- 输入: heights = [2, 4] -> 输出: 4
- 边界: [1] -> 1；[] -> 0；全相等 [3, 3, 3] -> 9

二、解法对比与复杂度（和 LC 42 接雨水对比记！）
- **LC 42 接雨水**：找两边**第一个比自己高**的柱子（凹槽蓄水） -> 用**单调递减栈**。
- **LC 84 最大矩形**：以当前柱子 `heights[i]` 为高，尽量向左右扩宽，直到遇到**第一个比自己矮**的柱子（短板拦住） -> 用**单调递增栈**！

1. 解法一（中心向两边扩展暴力版）:
   - 思路: 枚举每根柱子 `i` 作为矩形的高度，分别向左、向右找第一个 `< heights[i]` 的柱子下标 `left_smaller` 和 `right_smaller`，宽度就是 `right_smaller - left_smaller - 1`。
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(1)
2. 解法二（单调递增栈 + 前后哨兵 `0` - O(n) 最优经典模板）:
   - 思路: 在数组**首尾各补一个高度 `0` 的哨兵柱子**：
     - 尾部加 `0`：保证遍历结束时栈内所有还没结算的柱子都会被强行弹空结算（不用写收尾循环！）。
     - 头部加 `0`：保证栈永远不会空，弹出栈顶柱子 `mid` 后，`stack[-1]` 一定就是它左边第一个更矮的柱子 `left`！
     当新柱子 `heights[i] < heights[stack[-1]]` 时，说明栈顶柱子 `mid` 找到了右边第一个更矮的边界 `i`，立刻弹出并结算面积 `heights[mid] * (i - stack[-1] - 1)`。
   - 时间复杂度: O(n)，每根柱子最多入栈一次、出栈一次。
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- **OCR / 图像检测与数据网格最大可用区域**: 在二值化矩阵中找最大全 `1` 有效子矩阵（LC 85 最大矩形）正是逐行累计高度后直接调用 LC 84；内存碎片空闲块连续分配、K 线图有效支撑矩形面积估算也用此模型。
"""

from __future__ import annotations


def largest_rectangle_bruteforce(heights: list[int]) -> int:
    """解法一：枚举每根柱子向左右扩展找第一个更矮边界，O(n^2) 直观对照版。"""
    n = len(heights)
    best = 0
    for i, h in enumerate(heights):
        left = i - 1
        while left >= 0 and heights[left] >= h:
            left -= 1
        right = i + 1
        while right < n and heights[right] >= h:
            right += 1
        best = max(best, h * (right - left - 1))
    return best


def largest_rectangle_monotonic_stack(heights: list[int]) -> int:
    """解法二：单调递增栈 + 首尾补 0 哨兵，O(n) 时间一次扫描结算全部柱子。"""
    if not heights:
        return 0

    # 首尾补 0 哨兵：头部的 0 保证栈非空，尾部的 0 强制把所有残留柱子弹出结算
    padded = [0, *heights, 0]
    stack: list[int] = [0]
    best = 0

    for i in range(1, len(padded)):
        # 只要当前柱子更矮，栈顶柱子向右扩展的边界就已经到头了
        while padded[i] < padded[stack[-1]]:
            mid_idx = stack.pop()
            height = padded[mid_idx]
            left_idx = stack[-1]
            width = i - left_idx - 1  # 左右都不含两端更矮柱子本身
            best = max(best, height * width)
        stack.append(i)

    return best


def run_tests() -> None:
    """自动化断言测试，含递增、递减、平台、单柱与空数组。"""
    cases = [
        ([2, 1, 5, 6, 2, 3], 10),
        ([2, 4], 4),
        ([1, 2, 3, 4, 5], 9),
        ([5, 4, 3, 2, 1], 9),
        ([3, 3, 3, 3], 12),
        ([0, 9], 9),
        ([5], 5),
        ([], 0),
    ]
    for solver in (largest_rectangle_bruteforce, largest_rectangle_monotonic_stack):
        for heights, expected in cases:
            actual = solver(heights)
            assert actual == expected, f'{solver.__name__} 失败: {heights} -> {actual}'
    print('✅ LeetCode 84 (单调递增栈) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 84. 柱状图中最大的矩形 {'*' * 12}", sep='', end='\n\n')
    sample = [2, 1, 5, 6, 2, 3]
    print(f'柱子高度: {sample} -> 最大矩形面积: {largest_rectangle_monotonic_stack(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
