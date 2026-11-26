"""
[题目编号]: LeetCode 1143. 最长公共子序列 (Longest Common Subsequence / LCS)
[难度]: Medium (二维字符串 DP；与编辑距离、LIS 并列的序列对齐核心)
[所属专题]: 10_dynamic_programming
[前置知识]: 10_dynamic_programming/02_lc0072_edit_distance

一、题目描述
给定两个字符串 `text1` 和 `text2`，返回这两个字符串的最长公共子序列的长度。若不存在公共子序列，返回 0。
子序列不要求连续，但必须保持相对顺序。

示例:
- "abcde", "ace" -> 3
- "abc", "abc" -> 3
- "abc", "def" -> 0

二、解法
`dp[i][j]` = text1 前 i 与 text2 前 j 的 LCS 长度。
- 若 text1[i-1] == text2[j-1]: `dp[i][j] = dp[i-1][j-1] + 1`
- 否则: `dp[i][j] = max(dp[i-1][j], dp[i][j-1])`
时间 O(m*n)，空间 O(m*n)（可压到 O(min(m,n))）。

与编辑距离关系: 若只允许删除，编辑距离与 LCS 满足 `m + n - 2*LCS`。

三、工程映射
- Diff / 序列对齐 / RAG 证据对齐: Git diff、DNA 比对、两边文档共同要点抽取的基础模型。
"""

from __future__ import annotations


def longest_common_subsequence(text1: str, text2: str) -> int:
    """二维 DP 求 LCS 长度。"""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def run_tests() -> None:
    assert longest_common_subsequence('abcde', 'ace') == 3
    assert longest_common_subsequence('abc', 'abc') == 3
    assert longest_common_subsequence('abc', 'def') == 0
    assert longest_common_subsequence('', 'abc') == 0
    assert longest_common_subsequence('abc', '') == 0
    assert longest_common_subsequence('bsbininm', 'jmjkbkjkv') == 1
    print('✅ LeetCode 1143 (最长公共子序列 LCS) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 1143. 最长公共子序列 {'*' * 12}", sep='', end='\n\n')
    print(longest_common_subsequence('abcde', 'ace'))
    run_tests()


if __name__ == '__main__':
    bootstrap()
