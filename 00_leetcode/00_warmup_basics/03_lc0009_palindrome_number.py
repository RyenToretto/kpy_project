"""
[题目编号]: LeetCode 9. 回文数 (Palindrome Number)
[难度]: Easy
[所属专题]: 00_warmup_basics
[前置知识]: 00_basic/chapter02_var/exp_str.py (字符串切片反转)、while 循环、`//` 与 `%`

一、题目描述
给你一个整数 `x`，如果 `x` 是一个回文整数（正着读和倒着读都一样），返回 `True`；否则返回 `False`。

示例:
- 输入: x = 121 -> 输出: True
- 输入: x = -121 -> 输出: False (从左向右读是 -121，从右向左读是 121-)
- 输入: x = 10 -> 输出: False
- 边界: 0 -> True；个位数 7 -> True；大回文数 1234321 -> True

二、解法对比与复杂度
1. 解法一（Python 字符串切片版）:
   - 思路: 直接转成字符串 `s = str(x)`，比较 `s == s[::-1]`。
   - 时间复杂度: O(d)，d 为数字位数。
   - 空间复杂度: O(d)，需要额外字符串内存。
2. 解法二（不转字符串的进阶数学版：只反转后半段数字）:
   - 思路:
     - 负数一定不是回文数；
     - 末尾是 0 且自身不是 0 的数（如 10, 100）一定不是回文数（因为最高位不可能是 0）；
     - 不断把 `x % 10` 取出来拼接到 `reversed_half` 上，直到 `x <= reversed_half` 为止，说明已经处理了一半位数！
     - 偶数位看 `x == reversed_half`（如 1221 -> 12 == 12），奇数位看 `x == reversed_half // 10`（如 12321 -> 12 == 123 // 10）。
   - 时间复杂度: O(log10(x))，只循环位数的一半。
   - 空间复杂度: O(1)，纯数学计算，零额外字符串分配。

三、工程与 AI/大数据实战映射
- 高并发/低内存场景: 解法二展示了「不需要把数字变成字符串，仅靠原地数学拆位与折半」的思想，在高性能解析与溢出防御中非常经典。
"""

from __future__ import annotations


def is_palindrome_str(x: int) -> bool:
    """解法一：结合 00_basic/chapter02_var/exp_str.py 的切片反转技巧，最简单直观。"""
    if x < 0:
        return False
    text = str(x)
    return text == text[::-1]


def is_palindrome_math(x: int) -> bool:
    """解法二：不转字符串，只反转数字的后半部分，空间复杂度 O(1)。"""
    # 负数肯定不是；末尾为 0 但本身不为 0 的数也不可能是回文数
    if x < 0 or (x % 10 == 0 and x != 0):
        return False

    reversed_half = 0
    while x > reversed_half:
        last_digit = x % 10  # 取出当前最后一位
        reversed_half = reversed_half * 10 + last_digit  # 拼到反转数后面
        x //= 10  # 去掉最后一位

    # 奇数长度时，中间那位留在 reversed_half 的最后一位，通过 // 10 去掉后再比较
    return x == reversed_half or x == reversed_half // 10


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        (121, True),
        (-121, False),
        (10, False),
        (0, True),
        (7, True),
        (1221, True),
        (12321, True),
        (12345, False),
    ]
    for solver in (is_palindrome_str, is_palindrome_math):
        for x, expected in cases:
            actual = solver(x)
            assert actual == expected, f'{solver.__name__} 失败: x={x}, 实际={actual}'
    print('✅ LeetCode 9 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 9. 回文数 {'*' * 12}", sep='', end='\n\n')
    for sample in (121, -121, 10, 12321):
        print(f'{sample} 是回文数吗? -> {is_palindrome_math(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
