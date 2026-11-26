"""
[题目编号]: LeetCode 307. 区域和检索 - 数组可修改 (Range Sum Query - Mutable / 树状数组 BIT)
[难度]: Medium / 高阶数据结构门槛 (参考 kamyu104 Fenwick Tree / BIT O(n) 建树重写为 Python 3.12 教学版)
[所属专题]: 14_hard_capstones
[前置知识]: 13_bit_and_math (位运算 `i & -i`)、前缀和思想

一、题目描述
给你一个数组 `nums`，请你完成两类高频操作：
1. `update(index, val)`: 将 `nums[index]` 的值更新为 `val`。
2. `sum_range(left, right)`: 返回区间 `[left, right]` 内元素的总和。

为什么普通「前缀和数组」不行？如果数组经常被修改，每次 `update` 后重建整个前缀和数组要花 `O(n)`；而如果只存原数组，每次 `sum_range` 累加也要花 `O(n)`。当更新与查询混合出现几十万次时，两者都会超时！

二、解法对比与复杂度
1. 解法一（直接数组 - 查询 O(n) / 更新 O(1)）:
   - 仅作直观对照与小数据对拍。
2. 解法二（树状数组 Fenwick Tree / Binary Indexed Tree, BIT - 更新 O(log n) / 查询 O(log n)）:
   - 核心魔法：`lowbit(i) = i & -i`（提取二进制最低位的 `1` 所代表的值，如 `6 (110)` -> `2 (10)`）。
   - 下标从 `1` 开始的数组 `tree[i]` 只负责存「以 `i` 结尾、长度为 `lowbit(i)`」的这一小段区间和！
   - **单点增加 `delta`**: 沿着父节点 `i += (i & -i)` 一路向上补差值，最多改 `log2(n)` 个格子！
   - **前缀求和 `1..i`**: 沿着 `i -= (i & -i)` 一路拆出拼成 `[1..i]` 的几块区间并累加，最多加 `log2(n)` 次！
   - **O(n) 快速建树技巧（借鉴 kamyu104）**：每个节点 `i` 直接把自己的值加给直接父节点 `i + (i & -i)`，比逐个调用 `add` 建树 (`O(n log n)`) 更快。
   - 时间复杂度: 建树 O(n)，`update` 和 `sum_range` 均 O(log n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- **实时计数器 / 排行榜与动态前缀采样**: 如在线广告实时分桶曝光累计与范围求和、加权随机采样中的动态前缀概率表（动态改某个类别权重后快速按区间采样）。
"""

from __future__ import annotations


class NumArrayNaive:
    """解法一：普通列表直接修改与切片求和，更新 O(1)、查询 O(n)。"""

    def __init__(self, nums: list[int]) -> None:
        self._nums = list(nums)

    def update(self, index: int, val: int) -> None:
        self._nums[index] = val

    def sum_range(self, left: int, right: int) -> int:
        return sum(self._nums[left:right + 1])


class NumArrayBIT:
    """解法二：树状数组 (Fenwick Tree)，支持 O(log n) 单点修改与 O(log n) 区间求和。"""

    def __init__(self, nums: list[int]) -> None:
        self._nums = list(nums)
        n = len(nums)
        # tree 下标从 1 开始，下标 0 留作哨兵位避免 i & -i 死循环
        self._tree = [0] * (n + 1)
        for i, val in enumerate(nums, start=1):
            self._tree[i] += val
            parent = i + (i & -i)  # 直接父节点负责包含当前这段区间的更大块
            if parent <= n:
                self._tree[parent] += self._tree[i]

    def _add(self, index: int, delta: int) -> None:
        """给原数组 index 位置增加差值 delta（0-indexed 输入，内部转为 1-indexed）。"""
        pos = index + 1
        n = len(self._nums)
        while pos <= n:
            self._tree[pos] += delta
            pos += pos & -pos  # 跳到包含当前块的上级节点

    def _prefix_sum(self, index: int) -> int:
        """查询原数组 [0..index] 的前缀和（index < 0 时返回 0）。"""
        pos = index + 1
        total = 0
        while pos > 0:
            total += self._tree[pos]
            pos -= pos & -pos  # 剥掉最低位 1，继续累加更靠左的块
        return total

    def update(self, index: int, val: int) -> None:
        """将 nums[index] 改成 val：算出变化量 delta 后沿树状数组更新。"""
        delta = val - self._nums[index]
        if delta != 0:
            self._nums[index] = val
            self._add(index, delta)

    def sum_range(self, left: int, right: int) -> int:
        """区间 [left, right] 和 = prefix(right) - prefix(left - 1)。"""
        return self._prefix_sum(right) - self._prefix_sum(left - 1)


def run_tests() -> None:
    """自动化断言测试，含对拍随机交错更新查询与边界测试。"""
    # 1. 官方典型交互
    for impl in (NumArrayNaive, NumArrayBIT):
        arr = impl([1, 3, 5])
        assert arr.sum_range(0, 2) == 9
        arr.update(1, 2)  # [1, 2, 5]
        assert arr.sum_range(0, 2) == 8
        assert arr.sum_range(1, 1) == 2
        assert arr.sum_range(0, 0) == 1

    # 2. 边界：空数组、单元素、负数、连续多次改同一位置
    empty_bit = NumArrayBIT([])
    assert empty_bit._prefix_sum(-1) == 0

    single_bit = NumArrayBIT([-7])
    assert single_bit.sum_range(0, 0) == -7
    single_bit.update(0, 10)
    assert single_bit.sum_range(0, 0) == 10

    # 3. 与暴力版全量对拍（跨多个长度包含 2 的幂和非 2 的幂）
    init = [3, -1, 4, 1, 5, -9, 2, 6, 5]
    naive = NumArrayNaive(init)
    bit = NumArrayBIT(init)
    ops = [
        ('sum', 0, 8),
        ('upd', 3, 100),
        ('sum', 2, 5),
        ('upd', 0, -50),
        ('upd', 8, 0),
        ('sum', 0, 8),
        ('sum', 4, 7),
    ]
    for op, a, b in ops:
        if op == 'upd':
            naive.update(a, b)
            bit.update(a, b)
        else:
            assert naive.sum_range(a, b) == bit.sum_range(a, b), f'区间 [{a}, {b}] 对拍不一致'

    print('✅ LeetCode 307 (树状数组 BIT) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 307. 区域和检索 - 树状数组 BIT {'*' * 12}", sep='', end='\n\n')
    bit = NumArrayBIT([1, 3, 5, 7, 9])
    print('初始 [0..4] 和:', bit.sum_range(0, 4))
    bit.update(2, 10)
    print('把下标 2 改为 10 后 [1..3] 和:', bit.sum_range(1, 3))
    run_tests()


if __name__ == '__main__':
    bootstrap()
