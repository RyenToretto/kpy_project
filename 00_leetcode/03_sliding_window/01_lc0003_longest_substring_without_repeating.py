"""
[题目编号]: LeetCode 3. 无重复字符的最长子串 (Longest Substring Without Repeating Characters)
[难度]: Medium (面试出现率最高的中等题之一)
[所属专题]: 03_sliding_window
[前置知识]: set / dict、enumerate()、滑动窗口双指针

一、题目描述
给定一个字符串 `s`，请你找出其中不含有重复字符的「最长连续子串」的长度。

示例:
- 输入: s = "abcabcbb" -> 输出: 3 ("abc")
- 输入: s = "bbbbb" -> 输出: 1 ("b")
- 输入: s = "pwwkew" -> 输出: 3 ("wke"，注意 "pwke" 是子序列不是连续子串)
- 边界: "" -> 0；"a" -> 1；"abba" -> 2 (经典回退陷阱用例！)

二、解法对比与复杂度
1. 解法一（set 集合变长滑窗 - 最稳通用模板）:
   - 思路: 用集合 `window` 存当前 `[left, right]` 里的字符。当新字符 `s[right]` 已经在 `window` 里时，不断移除 `s[left]` 并右移 `left`，直到没有重复为止。
   - 时间复杂度: O(n)（每个字符最多进集合一次、出集合一次）
   - 空间复杂度: O(k)，k 为字符集去重大小
2. 解法二（dict 记录字符最近下标 - 一步跳转优化）:
   - 思路: 用 `last_seen[ch]` 记下每个字符最后一次出现的下标。当遇到重复字符且它的旧位置还在当前窗口内（`last_seen[ch] >= left`）时，直接把 `left` 跳到 `last_seen[ch] + 1`。
   - 避坑关键: 必须取 `max(left, last_seen[ch] + 1)`！例如 `"abba"` 读到第二个 `'a'` 时，`'a'` 上次在下标 0，但 `left` 已经在下标 2，绝对不能倒退回去！

三、工程与 AI/大数据实战映射
- RAG 文本切分 (Chunking) 与流式去重: 对连续 token / 文本流做滑动窗口切分与重复句检测时，核心窗口指针控制完全一致。
"""

from __future__ import annotations


def length_of_longest_substring_set(s: str) -> int:
    """解法一：使用 set 的标准滑动窗口模板，逻辑极其好理解。"""
    window: set[str] = set()
    left = 0
    best = 0

    for right, ch in enumerate(s):
        # 只要窗口里还有 ch，就一直把左边吐出去
        while ch in window:
            window.remove(s[left])
            left += 1
        window.add(ch)
        best = max(best, right - left + 1)

    return best


def length_of_longest_substring_dict(s: str) -> int:
    """解法二：用 dict 直接把 left 跳到重复字符下一位，注意不能让 left 倒退。"""
    last_seen: dict[str, int] = {}
    left = 0
    best = 0

    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1  # 直接跨过上次重复位置
        last_seen[ch] = right
        best = max(best, right - left + 1)

    return best


def run_tests() -> None:
    """自动化断言测试，特别包含 "abba" 防止 left 倒退 bug。"""
    cases = [
        ('abcabcbb', 3),
        ('bbbbb', 1),
        ('pwwkew', 3),
        ('', 0),
        ('a', 1),
        ('abba', 2),
        ('dvdf', 3),
    ]
    for solver in (length_of_longest_substring_set, length_of_longest_substring_dict):
        for s, expected in cases:
            actual = solver(s)
            assert actual == expected, f'{solver.__name__} 失败: s={s!r}, 实际={actual}'
    print('✅ LeetCode 3 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 3. 无重复字符的最长子串 {'*' * 12}", sep='', end='\n\n')
    for text in ('abcabcbb', 'pwwkew', 'abba'):
        print(f'{text!r} -> 最长无重复子串长度 = {length_of_longest_substring_dict(text)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
