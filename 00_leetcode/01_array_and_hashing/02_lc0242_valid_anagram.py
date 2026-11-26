"""
[题目编号]: LeetCode 242. 有效的字母异位词 (Valid Anagram)
[难度]: Easy
[所属专题]: 01_array_and_hashing
[前置知识]: dict 计数、collections.Counter、sorted()

一、题目描述
给定两个字符串 `s` 和 `t`，如果 `t` 是 `s` 的字母异位词（两个字符串包含的字符种类和每个字符出现次数完全相同，只是顺序不同），返回 `True`；否则返回 `False`。

示例:
- 输入: s = "anagram", t = "nagaram" -> 输出: True
- 输入: s = "rat", t = "car" -> 输出: False
- 边界: 长度不同直接 False；空串 ("", "") -> True；中文或 Unicode 字符也能支持

二、解法对比与复杂度
1. 解法一（排序对比）:
   - 思路: 两个字母异位词排序后必然一模一样。
   - 时间复杂度: O(n log n)
   - 空间复杂度: O(n)
2. 解法二（手动 dict 加减计数 - 面试核心）:
   - 思路: 先判断长度是否相等；再用一个字典记录 `s` 中每个字符出现次数 `+1`，遍历 `t` 时 `-1`，若某字符减到小于 0 或不存在直接返回 `False`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(k)，k 为字符集大小（小写字母最多 26，可视为 O(1)）。
3. 解法三（标准库 Counter 版）:
   - 思路: `Counter(s) == Counter(t)`，简洁可读性强。

三、工程与 AI/大数据实战映射
- 词袋模型 (Bag-of-Words) 与文本相似度: 不看词序只比较词频分布，是传统 NLP、关键词匹配以及下一题「49. 字母异位词分组」的基础。
"""

from __future__ import annotations

from collections import Counter


def is_anagram_sort(s: str, t: str) -> bool:
    """解法一：排序后直接比较，代码极短但时间复杂度为 O(n log n)。"""
    if len(s) != len(t):
        return False
    return sorted(s) == sorted(t)


def is_anagram_dict(s: str, t: str) -> bool:
    """解法二：手写哈希字典计数，O(n) 时间且通用支持任意 Unicode 字符。"""
    if len(s) != len(t):
        return False

    counts: dict[str, int] = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1  # .get(ch, 0) 避免 key 不存在报错

    for ch in t:
        if ch not in counts or counts[ch] == 0:
            return False
        counts[ch] -= 1

    return True


def is_anagram_counter(s: str, t: str) -> bool:
    """解法三：Python 标准库 Counter 一行比较频次。"""
    return len(s) == len(t) and Counter(s) == Counter(t)


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('anagram', 'nagaram', True),
        ('rat', 'car', False),
        ('a', 'ab', False),
        ('', '', True),
        ('你好世界', '界世好你', True),
    ]
    for solver in (is_anagram_sort, is_anagram_dict, is_anagram_counter):
        for s, t, expected in cases:
            assert solver(s, t) is expected, f'{solver.__name__} 失败: s={s}, t={t}'
    print('✅ LeetCode 242 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 242. 有效的字母异位词 {'*' * 12}", sep='', end='\n\n')
    print(f'"anagram" 与 "nagaram": {is_anagram_dict("anagram", "nagaram")}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
