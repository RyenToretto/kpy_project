"""
[题目编号]: LeetCode 76. 最小覆盖子串 (Minimum Window Substring)
[难度]: Hard (第 1 道经典 Hard 模板题)
[所属专题]: 03_sliding_window
[前置知识]: Counter、dict 滑动窗口计数

一、题目描述
给你一个字符串 `s` 和一个字符串 `t`。返回 `s` 中涵盖 `t` 所有字符（包括重复字符数量）的**最短连续子串**；如果不存在，返回空字符串 `""`。

示例:
- 输入: s = "ADOBECODEBANC", t = "ABC" -> 输出: "BANC"
- 输入: s = "a", t = "a" -> 输出: "a"
- 输入: s = "a", t = "aa" -> 输出: ""

二、解法与复杂度
- 思路（万能变长滑窗模板：先扩张找可行解，再收缩找最优解）:
  1. `need = Counter(t)` 记录目标字符串每种字符需要的个数；`valid` 记录目前窗口里「有多少种字符已经达标」。
  2. `right` 不断向右扩大窗口：若新字符在 `need` 中，则 `window[ch] += 1`，当 `window[ch] == need[ch]` 时说明这一种字符凑齐了，`valid += 1`。
  3. 当 `valid == len(need)`（所有必需字符的个数全都达标）时：
     - 先记录当前更短的窗口 `(start, min_len)`；
     - 再尝试从左边弹出 `s[left]` 并 `left += 1` 看看能不能更短；若移出后导致某必需字符不达标，则 `valid -= 1`，跳出收缩继续扩张 `right`。
- 时间复杂度: O(|s| + |t|)
- 空间复杂度: O(|s| + |t|)（字符集常数空间）

三、工程与 AI/大数据实战映射
- 搜索引擎摘要生成 (Snippet Extraction): 搜索多个关键词时，如何在网页正文中定位包含全部检索词的最短上下文片段？核心算法就是本题的最小覆盖子串！
"""

from __future__ import annotations

from collections import Counter


def min_window(s: str, t: str) -> str:
    """经典 Hard 最小覆盖子串滑窗模板。"""
    if not s or not t or len(s) < len(t):
        return ''

    need = Counter(t)  # 目标字符需求表
    window: dict[str, int] = {}  # 当前窗口已收集的字符频次
    valid = 0  # 已满足需求数量的字符种类数

    left = 0
    best_start = 0
    best_len = float('inf')

    for right, ch in enumerate(s):
        # 1. 扩张窗口：只关心 t 中需要的字符
        if ch in need:
            window[ch] = window.get(ch, 0) + 1
            if window[ch] == need[ch]:
                valid += 1

        # 2. 当窗口已完全覆盖 t 时，尝试不断收缩左边界寻找更短答案
        while valid == len(need):
            current_len = right - left + 1
            if current_len < best_len:
                best_len = current_len
                best_start = left

            left_ch = s[left]
            left += 1
            if left_ch in need:
                # 若移走前正好刚达标，移走后就不再达标了
                if window[left_ch] == need[left_ch]:
                    valid -= 1
                window[left_ch] -= 1

    return '' if best_len == float('inf') else s[best_start : best_start + int(best_len)]


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('ADOBECODEBANC', 'ABC', 'BANC'),
        ('a', 'a', 'a'),
        ('a', 'aa', ''),
        ('aa', 'aa', 'aa'),
        ('cabwefgewcwaefgcf', 'cae', 'cwae'),
    ]
    for s, t, expected in cases:
        actual = min_window(s, t)
        assert actual == expected, f'失败: s={s!r}, t={t!r}, 实际={actual!r}, 期望={expected!r}'
    print('✅ LeetCode 76 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 76. 最小覆盖子串 (Hard) {'*' * 12}", sep='', end='\n\n')
    s, t = 'ADOBECODEBANC', 'ABC'
    print(f's={s!r}, t={t!r} -> 最小覆盖子串: {min_window(s, t)!r}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
