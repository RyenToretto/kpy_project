"""
[题目编号]: LeetCode 295. 数据流的中位数 (Find Median from Data Stream)
[难度]: Hard (大数据实时统计与系统设计经典 Hard)
[所属专题]: 14_hard_capstones
[前置知识]: heapq (小顶堆)、负数模拟大顶堆技巧

一、题目描述
中位数是有序整数列表中的中间值（如果个数是偶数，则是中间两个数的平均值）。
请你设计一个支持以下两种操作的数据结构：
- `add_num(num)`: 从实时数据流中添加一个整数到数据结构中；
- `find_median()`: 返回目前为止所有元素的中位数。

示例:
- add_num(1) -> add_num(2) -> find_median() == 1.5 -> add_num(3) -> find_median() == 2.0

二、解法与复杂度
- 思路（对顶双堆：左半边大顶堆 + 右半边小顶堆）:
  把所有已经到来的数字想象成从小到大排成一排，从正中间切一刀分成两半：
  1. `low`（左半边，较小的那一半）：用**大顶堆**存（Python 只有小顶堆 `heapq`，所以存 `-num` 来巧妙模拟大顶堆！），堆顶 `-low[0]` 就是左半边的最大值；
  2. `high`（右半边，较大的那一半）：用**小顶堆**存，堆顶 `high[0]` 就是右半边的最小值；
  3. 保持两大铁律不变：
     - **值域有序**：`low` 里的所有数 <= `high` 里的所有数；
     - **人数均衡**：允许 `len(low) == len(high)` 或 `len(low) == len(high) + 1`。
  4. 每次新数 `num` 到来，先推入 `low`，把 `low` 中最大的弹给 `high`（保证值域正确），如果此时 `len(high) > len(low)` 再把 `high` 最小的挪回 `low`（保证人数平衡）！
- 时间复杂度: `add_num` 为 O(log n)，`find_median` 为 O(1)！
- 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- **大数据流式计算 / APM 监控指标**: 在实时监控接口响应耗时 P50（中位数）或风控交易中位数时，数据每秒源源不断进来，不可能每次都重新 `sort()`！对顶双堆正是实时求分位数的经典原型。
"""

from __future__ import annotations

import heapq


class MedianFinder:
    """对顶双堆实时维护数据流中位数。"""

    def __init__(self) -> None:
        # low 保存较小的一半（存负数以用 heapq 模拟大顶堆）
        self.low: list[int] = []
        # high 保存较大的一半（原生小顶堆）
        self.high: list[int] = []

    def add_num(self, num: int) -> None:
        # 1. 先放进左半边大顶堆，并把左半边最大的值挤到右半边小顶堆，维持 low <= high
        heapq.heappush(self.low, -num)
        largest_in_low = -heapq.heappop(self.low)
        heapq.heappush(self.high, largest_in_low)

        # 2. 保持平衡：始终保证 len(low) >= len(high)，且最多多 1 个元素
        if len(self.high) > len(self.low):
            smallest_in_high = heapq.heappop(self.high)
            heapq.heappush(self.low, -smallest_in_high)

    def find_median(self) -> float:
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0


def run_tests() -> None:
    """自动化断言测试。"""
    finder = MedianFinder()
    finder.add_num(1)
    assert finder.find_median() == 1.0
    finder.add_num(2)
    assert finder.find_median() == 1.5
    finder.add_num(3)
    assert finder.find_median() == 2.0
    finder.add_num(10)
    assert finder.find_median() == 2.5

    # 验证乱序与负数数据流
    finder2 = MedianFinder()
    for x in (5, -2, 100, 0, 5):
        finder2.add_num(x)
    assert finder2.find_median() == 5.0
    print('✅ LeetCode 295 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 295. 数据流的中位数 (Hard) {'*' * 12}", sep='', end='\n\n')
    finder = MedianFinder()
    for num in (5, 1, 10, 2):
        finder.add_num(num)
        print(f'流入数字 {num:>2} -> 当前实时中位数: {finder.find_median()}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
