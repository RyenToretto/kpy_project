"""
[题目编号]: LeetCode 435. 无重叠区间 (Non-overlapping Intervals)
[难度]: Medium (与 LC 56 合并区间互补：删最少区间使无重叠)
[所属专题]: 09_greedy
[前置知识]: 09_greedy/00_lc0056_merge_intervals

一、题目描述
给定一个区间的集合 `intervals`，其中 `intervals[i] = [start_i, end_i]`。
返回需要移除区间的最小数量，使剩余区间互不重叠。（端点相等不算重叠）

示例:
- [[1, 2], [2, 3], [3, 4], [1, 3]] -> 1 (移除 [1, 3])
- [[1, 2], [1, 2], [1, 2]] -> 2
- [[1, 2], [2, 3]] -> 0

二、解法
按右端点升序排序；贪心保留「结束最早」的区间，这样给后面留出最多空间。
每当下一个区间左端点 < 当前保留区间右端点，就发生重叠，必须删掉（计数 +1）。
时间 O(n log n)，空间 O(1)。

与 LC 56: 56 是合并重叠；435 是删除最少使不重叠。

三、工程映射
- 会议室 / 任务去冲突: 删掉最少会议使日程无冲突；RAG 重叠 chunk 去重时保留结束最早的片段。
"""

from __future__ import annotations


def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    """按右端点排序，贪心保留结束最早的区间。"""
    if not intervals:
        return 0
    ordered = sorted(intervals, key=lambda item: item[1])
    kept_end = ordered[0][1]
    removed = 0
    for start, end in ordered[1:]:
        if start < kept_end:
            removed += 1  # 与已保留区间重叠，删当前
        else:
            kept_end = end
    return removed


def run_tests() -> None:
    assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
    assert erase_overlap_intervals([[1, 2], [1, 2], [1, 2]]) == 2
    assert erase_overlap_intervals([[1, 2], [2, 3]]) == 0
    assert erase_overlap_intervals([]) == 0
    assert erase_overlap_intervals([[1, 100], [2, 3], [3, 4]]) == 1
    print('✅ LeetCode 435 (无重叠区间) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 435. 无重叠区间 {'*' * 12}", sep='', end='\n\n')
    print(erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
