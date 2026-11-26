"""
[题目编号]: LeetCode 28. 找出字符串中第一个匹配项的下标 (Find the Index of the First Occurrence in a String / KMP)
[难度]: Medium (字符串匹配经典 KMP 模板，参考 kamyu104 KMP 前缀表思路重写为 Python 3.12 教学版)
[所属专题]: 02_two_pointers
[前置知识]: 字符串索引、双指针、`for` 与 `while` 循环

一、题目描述
给你两个字符串 `haystack`（文本串）和 `needle`（模式串），请你在 `haystack` 中找出 `needle` 串出现的第一个位置（下标从 0 开始）。如果不存在，则返回 `-1`；若 `needle` 为空串则返回 `0`。

示例:
- 输入: haystack = "sadbutsad", needle = "sad" -> 输出: 0
- 输入: haystack = "leetcode", needle = "leeto" -> 输出: -1
- 边界: needle="" -> 0；needle 比 haystack 长 -> -1；高度重复串 "aaaaa...b" 匹配 "aaab"

二、解法对比与复杂度
1. 解法一（朴素双指针暴力匹配 - 容易退化）:
   - 思路: 枚举文本串每个起点 `i`，逐字符比对；一旦失配，文本指针退回 `i + 1`、模式指针退回 `0` 重新来。
   - 最坏时间复杂度: O(n * m)（例如文本 `"aaaa...ab"` 配 `"aaab"` 时每次都在最后一位失配）。
   - 空间复杂度: O(1)
2. 解法二（KMP 算法：构建前缀表 LPS / Next 数组，主串指针永不回退）:
   - 思路: 失配时为什么不用从头再比？因为刚刚已经匹配成功的那一段前缀里，往往存在「既是前缀又是后缀」的相同片段（即最长公共前后缀 LPS）！
     例如模式串 `"aabaaf"`：当末尾 `'f'` 失配时，前面 `"aabaa"` 的最长相等前后缀是 `"aa"`（长度 2），所以模式串直接跳到下标 `2` 继续比较，文本串指针 `i` 一路向前绝不回头！
   - 时间复杂度: O(n + m)
   - 空间复杂度: O(m)（存放 `lps` 前缀表）

三、工程与 AI/大数据实战映射
- 大规模文本检索与敏感词/日志关键词扫描: KMP 保证流式字符一次扫描、无需回溯缓冲区；它的多模式扩展（AC 自动机 = Trie + KMP 失配指针）正是敏感词过滤、安全护栏 (Guardrail) 规则匹配的标准实现。
"""

from __future__ import annotations


def str_str_bruteforce(haystack: str, needle: str) -> int:
    """解法一：暴力双指针逐起点匹配，最坏时间 O(n * m)。"""
    if not needle:
        return 0
    n, m = len(haystack), len(needle)
    for start in range(n - m + 1):
        offset = 0
        while offset < m and haystack[start + offset] == needle[offset]:
            offset += 1
        if offset == m:
            return start
    return -1


def build_lps(pattern: str) -> list[int]:
    """构建 KMP 最长相等前后缀表 (LPS): lps[i] 表示 pattern[:i+1] 的最长真前后缀长度。"""
    lps = [0] * len(pattern)
    prefix_len = 0  # 当前已匹配的前缀长度（也是下一个待比较的前缀下标）

    for i in range(1, len(pattern)):
        # 如果当前字符不匹配，沿着已匹配前缀的最短可回退位置向前回退
        while prefix_len > 0 and pattern[i] != pattern[prefix_len]:
            prefix_len = lps[prefix_len - 1]
        if pattern[i] == pattern[prefix_len]:
            prefix_len += 1
        lps[i] = prefix_len

    return lps


def str_str_kmp(haystack: str, needle: str) -> int:
    """解法二：KMP 算法，时间复杂度严格 O(n + m)，主串指针永不后退。"""
    if not needle:
        return 0
    n, m = len(haystack), len(needle)
    if m > n:
        return -1

    lps = build_lps(needle)
    j = 0  # j 指向模式串 needle 当前等待匹配的下标

    for i in range(n):
        # 文本字符与模式字符不相等时，利用 lps 表只回退模式串指针 j
        while j > 0 and haystack[i] != needle[j]:
            j = lps[j - 1]
        if haystack[i] == needle[j]:
            j += 1
        if j == m:
            return i - m + 1  # 找到完整匹配，返回起始下标

    return -1


def run_tests() -> None:
    """自动化断言测试，含高度重复的 KMP 压测用例与前缀表核验。"""
    assert build_lps('aabaaf') == [0, 1, 0, 1, 2, 0]
    cases = [
        ('sadbutsad', 'sad', 0),
        ('leetcode', 'leeto', -1),
        ('hello', 'll', 2),
        ('aabaabaafa', 'aabaaf', 3),
        ('abc', '', 0),
        ('ab', 'abcd', -1),
        ('a' * 200 + 'b', 'a' * 20 + 'b', 180),
    ]
    for solver in (str_str_bruteforce, str_str_kmp):
        for haystack, needle, expected in cases:
            actual = solver(haystack, needle)
            assert actual == expected, f'{solver.__name__} 失败: {haystack!r}, {needle!r}, 实际={actual}'
    print('✅ LeetCode 28 (KMP) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 28. 字符串匹配 KMP {'*' * 12}", sep='', end='\n\n')
    pattern = 'aabaaf'
    print(f'模式串 {pattern!r} 的前缀表 LPS: {build_lps(pattern)}')
    print(f'在 "aabaabaafa" 中首次匹配位置: {str_str_kmp("aabaabaafa", pattern)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
