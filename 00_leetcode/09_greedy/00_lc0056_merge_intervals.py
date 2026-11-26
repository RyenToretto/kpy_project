"""
[题目编号]: LeetCode 56. 合并区间 (Merge Intervals)
[难度]: Medium (后端与数据处理极高频题)
[所属专题]: 09_greedy
[前置知识]: sorted(..., key=lambda x: x[0])、二维列表操作

一、题目描述
以数组 `intervals` 表示若干个区间的集合，其中单个区间为 `[start_i, end_i]`。
请你合并所有重叠的区间，并返回一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间。

示例:
- 输入: intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]
- 输出: [[1, 6], [8, 10], [15, 18]]  (因为 [1, 3] 和 [2, 6] 重叠)
- 边界: [[1, 4], [4, 5]] -> [[1, 5]] (端点相接也算重叠！)；[] -> []；[[1, 4], [2, 3]] -> [[1, 4]] (完全包含时右端点要取 max)

二、解法与复杂度
- 思路（先按起点排序，再线性贪心合并）:
  1. 先按每个区间的左端点 `interval[0]` 从小到大排序。
  2. 初始化 `merged = [ordered[0].copy()]`（复制一份区间，避免修改调用方传入的原列表）。
  3. 依次看下一个区间 `[start, end]`：
     - 如果 `start <= merged[-1][1]`（当前左端点 <= 上一个已合并区间的右端点），说明重叠了！直接把上一个区间的右端点拉宽：`merged[-1][1] = max(merged[-1][1], end)`；
     - 否则没有重叠，直接追加新区间。
- 时间复杂度: O(n log n)（主要花在排序上）
- 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- RAG 检索片段合并 (Contextual Segment Merging): 同一篇文档命中多个重叠的 Chunk `[start_char, end_char]` 时，必须先合并重叠区间再喂给大模型，省 Token 又防上下文割裂！
- 视频剪辑时间轴、会议室日程冲突合并也是完全相同的算法。
"""

from __future__ import annotations


def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """按区间起点排序后贪心合并重叠区间。"""
    if not intervals:
        return []

    # 按区间左端点升序排序（左端点相同时按右端点升序）
    ordered = sorted(intervals, key=lambda pair: (pair[0], pair[1]))
    merged: list[list[int]] = [ordered[0].copy()]

    for start, end in ordered[1:]:
        last_end = merged[-1][1]
        if start <= last_end:
            # 重叠：取两个右端点的较大值（注意 [1, 4] 包含 [2, 3] 的情况）
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])

    return merged


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
        ([[1, 4], [4, 5]], [[1, 5]]),
        ([[1, 4], [2, 3]], [[1, 4]]),
        ([[1, 4], [0, 4]], [[0, 4]]),
        ([], []),
    ]
    for raw, expected in cases:
        snapshot = [item.copy() for item in raw]
        actual = merge_intervals(snapshot)
        assert actual == expected, f'失败: 输入={raw}, 实际={actual}'
    print('✅ LeetCode 56 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 56. 合并区间 {'*' * 12}", sep='', end='\n\n')
    sample = [[1, 3], [2, 6], [8, 10], [15, 18]]
    print(f'原始区间: {sample}')
    print(f'合并结果: {merge_intervals(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
