"""
[题目编号]: LeetCode 49. 字母异位词分组 (Group Anagrams)
[难度]: Medium
[所属专题]: 01_array_and_hashing
[前置知识]: collections.defaultdict、tuple (元组可哈希作为字典 key)、ord()

一、题目描述
给你一个字符串数组 `strs`，请你将「字母异位词」组合在一起。可以按任意顺序返回结果列表。

示例:
- 输入: strs = ["eat", "tea", "tan", "ate", "nat", "bat"]
- 输出: [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]
- 边界: [""] -> [[""]]；["a"] -> [["a"]]；[] -> []

二、解法对比与复杂度
1. 解法一（排序字符串作为分组 Key）:
   - 思路: "eat"、"tea"、"ate" 排序后都变成 `"aet"`，把它作为 `defaultdict(list)` 的键，相同键归到一组。
   - 时间复杂度: O(n * k log k)，n 为单词个数，k 为单词最大长度。
   - 空间复杂度: O(n * k)
2. 解法二（26 位频次元组作为分组 Key - 理论最优）:
   - 思路: 用长度为 26 的数组统计 `a`~`z` 出现次数，再转成不可变的 `tuple(counts)`（因为 `list` 不能做字典的 key，而 `tuple` 可以！），避免了对每个单词排序。
   - 时间复杂度: O(n * (k + 26)) ≈ O(n * k)
   - 空间复杂度: O(n * k)

三、工程与 AI/大数据实战映射
- 分组聚合 (GroupBy): 在 Pandas/Spark 数据处理、日志归一化（把参数顺序不同的请求归为一类）中，「设计一个规范化 Key (Canonical Key)」是非常常见的工程技巧。
- Python 类型核心: 这道题正好帮你吃透 `list` 不可哈希（不能当 dict key）而 `tuple` 可哈希的本质区别！
"""

from __future__ import annotations

from collections import defaultdict


def group_anagrams_sort_key(strs: list[str]) -> list[list[str]]:
    """解法一：排序后转成字符串作为 Key，写法最清爽、最易记。"""
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for word in strs:
        key = ''.join(sorted(word))  # sorted(word) 返回字符列表，join 拼回字符串
        groups[key].append(word)
    return list(groups.values())


def group_anagrams_count_key(strs: list[str]) -> list[list[str]]:
    """解法二：用 26 个字母出现次数的 tuple 作为 Key，省去排序开销。"""
    groups: defaultdict[tuple[int, ...], list[str]] = defaultdict(list)
    for word in strs:
        counts = [0] * 26  # 索引 0~25 对应 'a'~'z'
        for ch in word:
            counts[ord(ch) - ord('a')] += 1
        # 注意：list 是可变对象不能做字典 Key，必须转成不可变的 tuple！
        groups[tuple(counts)].append(word)
    return list(groups.values())


def _normalize(result: list[list[str]]) -> list[list[str]]:
    """测试辅助：忽略组间与组内顺序，便于精确对比。"""
    return sorted([sorted(group) for group in result])


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        (
            ['eat', 'tea', 'tan', 'ate', 'nat', 'bat'],
            [['bat'], ['nat', 'tan'], ['ate', 'eat', 'tea']],
        ),
        ([''], [['']]),
        (['a'], [['a']]),
        ([], []),
    ]
    for solver in (group_anagrams_sort_key, group_anagrams_count_key):
        for strs, expected in cases:
            actual = solver(strs)
            assert _normalize(actual) == _normalize(expected), f'{solver.__name__} 失败: {actual}'
    print('✅ LeetCode 49 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 49. 字母异位词分组 {'*' * 12}", sep='', end='\n\n')
    sample = ['eat', 'tea', 'tan', 'ate', 'nat', 'bat']
    print(f'分组结果: {group_anagrams_count_key(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
