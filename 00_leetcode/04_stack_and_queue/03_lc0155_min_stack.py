"""
[题目编号]: LeetCode 155. 最小栈 (Min Stack)
[难度]: Medium (辅助栈同步维护最小值)
[所属专题]: 04_stack_and_queue
[前置知识]: list 模拟栈、04_stack_and_queue/00_lc0020

一、题目描述
设计一个支持 `push`、`pop`、`top`，并能在常数时间内检索到最小元素的栈：
- `push(val)` / `pop()` / `top()` 与普通栈相同；
- `get_min()` 返回栈中最小元素，要求 O(1)。

二、解法对比
1. 每次 get_min 扫一遍: O(n)，不满足题意。
2. 双栈同步: `data` 存真实值；`mins` 存「当前栈状态下的最小值」。
   - push: 入 data；同时 `mins.append(min(val, mins[-1] if mins else val))`
   - pop: 两个栈一起弹
   - get_min: 直接看 `mins[-1]`
   - 时间全 O(1)，空间 O(n)

三、工程映射
- 实时监控栈式上下文: 嵌套事务/嵌套 span 中随时拿到当前上下文内的最低水位（如最低余额、最小优先级）。
"""

from __future__ import annotations


class MinStackScan:
    """直观版：get_min 线性扫描，仅作对照。"""

    def __init__(self) -> None:
        self._data: list[int] = []

    def push(self, val: int) -> None:
        self._data.append(val)

    def pop(self) -> None:
        self._data.pop()

    def top(self) -> int:
        return self._data[-1]

    def get_min(self) -> int:
        return min(self._data)


class MinStack:
    """最优版：辅助栈同步最小值，get_min 为 O(1)。"""

    def __init__(self) -> None:
        self._data: list[int] = []
        self._mins: list[int] = []

    def push(self, val: int) -> None:
        self._data.append(val)
        prev = self._mins[-1] if self._mins else val
        self._mins.append(val if val < prev else prev)

    def pop(self) -> None:
        self._data.pop()
        self._mins.pop()

    def top(self) -> int:
        return self._data[-1]

    def get_min(self) -> int:
        return self._mins[-1]


def run_tests() -> None:
    for cls in (MinStackScan, MinStack):
        stack = cls()
        stack.push(-2)
        stack.push(0)
        stack.push(-3)
        assert stack.get_min() == -3
        stack.pop()
        assert stack.top() == 0
        assert stack.get_min() == -2
        stack.push(-1)
        assert stack.get_min() == -2
        assert stack.top() == -1
    print('✅ LeetCode 155 (最小栈) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 155. 最小栈 {'*' * 12}", sep='', end='\n\n')
    stack = MinStack()
    for val in [3, 1, 2]:
        stack.push(val)
        print(f'push {val}, min={stack.get_min()}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
