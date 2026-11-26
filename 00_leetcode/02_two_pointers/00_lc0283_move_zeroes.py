"""
[题目编号]: LeetCode 283. 移动零 (Move Zeroes)
[难度]: Easy
[所属专题]: 02_two_pointers
[前置知识]: 列表索引、Python 原地交换 `a, b = b, a`

一、题目描述
给定一个数组 `nums`，编写一个函数将所有 `0` 移动到数组的末尾，同时**保持非零元素的相对顺序**。
注意：必须在不复制数组的情况下原地对数组进行操作。

示例:
- 输入: [0, 1, 0, 3, 12] -> 原地变为 [1, 3, 12, 0, 0]
- 边界: [0] -> [0]；[1, 2, 3] -> [1, 2, 3]；[] -> []

二、解法对比与复杂度
1. 解法一（二次遍历：先填非零，后面全补 0）:
   - 思路: `slow` 记录下一个非零数该放的位置。先遍历把所有非零数紧凑搬到前面，最后把 `[slow:]` 全设为 `0`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)
2. 解法二（一次遍历快慢指针交换 - 经典最优）:
   - 思路: `fast` 扫到非零数时，直接和 `nums[slow]` 交换，然后 `slow += 1`。
     可以理解为：`[0, slow)` 区间永远是已经排好的非零数，`[slow, fast)` 区间全是 `0`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 内存受限的原地数据清洗 / 稀疏特征压缩: 在嵌入式或大规模数组处理中，不申请新数组而做原地过滤压缩（Compaction），原理与快慢指针一致。
"""

from __future__ import annotations


def move_zeroes_fill(nums: list[int]) -> None:
    """解法一：先紧凑前移非零元素，再把剩余位置统一置 0。"""
    slow = 0
    for num in nums:
        if num != 0:
            nums[slow] = num
            slow += 1

    while slow < len(nums):
        nums[slow] = 0
        slow += 1


def move_zeroes_swap(nums: list[int]) -> None:
    """解法二：快慢指针一次遍历原地交换。"""
    slow = 0  # slow 指向下一个“非零元素应该落位”的下标
    for fast in range(len(nums)):
        if nums[fast] != 0:
            # 只有当 fast != slow 时才真的需要交换，省去无意义的自我赋值
            if fast != slow:
                nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([0, 1, 0, 3, 12], [1, 3, 12, 0, 0]),
        ([0], [0]),
        ([1, 2, 3], [1, 2, 3]),
        ([0, 0, 1], [1, 0, 0]),
        ([], []),
    ]
    for solver in (move_zeroes_fill, move_zeroes_swap):
        for raw, expected in cases:
            arr = raw.copy()  # 复制一份做原地修改测试，避免污染原始用例
            solver(arr)
            assert arr == expected, f'{solver.__name__} 失败: 输入={raw}, 实际={arr}'
    print('✅ LeetCode 283 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 283. 移动零 {'*' * 12}", sep='', end='\n\n')
    data = [0, 1, 0, 3, 12]
    print(f'移动前: {data}')
    move_zeroes_swap(data)
    print(f'移动后: {data}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
