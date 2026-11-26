"""
[题目编号]: LeetCode 136. 只出现一次的数字 (Single Number)
[难度]: Easy (位运算异或入门魔法)
[所属专题]: 13_bit_and_math
[前置知识]: 位异或运算符 `^`、set / Counter 对照

一、题目描述
给你一个非空整数数组 `nums`，除了某个元素只出现一次以外，其余每个元素均出现两次。找出那个只出现了一次的元素。
进阶要求：设计并实现线性时间复杂度 O(n) 且仅使用常量额外空间 O(1) 的算法。

示例:
- 输入: [2, 2, 1] -> 输出: 1
- 输入: [4, 1, 2, 1, 2] -> 输出: 4
- 边界: [1] -> 1；包含负数 [-1, -1, 9] -> 9

二、解法对比与复杂度
1. 解法一（哈希计数版 - 通用但需要 O(n) 空间）:
   - 思路: 用 `Counter` 统计，找出出现次数为 1 的那个数。
2. 解法二（异或 XOR 魔法 - O(n) 时间 + O(1) 空间）:
   - 记住异或运算 `^` 的三条黄金定律（相异为 1，相同为 0）：
     1) 任何数和自己异或都是 0：`a ^ a = 0`
     2) 任何数和 0 异或都是它本身：`a ^ 0 = a`
     3) 异或满足交换律与结合律：`a ^ b ^ a = (a ^ a) ^ b = 0 ^ b = b`
   - 所以把数组里所有数全部异或一遍，成对出现的全部互相抵消成 0，最后剩下的唯一数字就是答案！

三、工程与 AI/大数据实战映射
- 分布式数据校验 / RAID 奇偶校验与通信纠错: 异或运算是底层存储纠错码、分布式一致性校验和轻量加密混淆最常用的比特级原语。
"""

from __future__ import annotations

from collections import Counter


def single_number_counter(nums: list[int]) -> int:
    """解法一：哈希计数，容易想到但需要 O(n) 额外空间。"""
    counts = Counter(nums)
    for num, freq in counts.items():
        if freq == 1:
            return num
    raise ValueError('输入数组中不存在只出现一次的元素')


def single_number_xor(nums: list[int]) -> int:
    """解法二：全部元素连续做异或运算，O(n) 时间 + O(1) 空间最优解。"""
    acc = 0
    for num in nums:
        acc ^= num  # 成对元素会自动抵消为 0
    return acc


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([2, 2, 1], 1),
        ([4, 1, 2, 1, 2], 4),
        ([1], 1),
        ([-1, -1, 9], 9),
    ]
    for solver in (single_number_counter, single_number_xor):
        for nums, expected in cases:
            assert solver(nums) == expected, f'{solver.__name__} 失败: {nums}'
    print('✅ LeetCode 136 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 136. 只出现一次的数字 {'*' * 12}", sep='', end='\n\n')
    sample = [4, 1, 2, 1, 2]
    print(f'{sample} 中唯一落单的数字: {single_number_xor(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
