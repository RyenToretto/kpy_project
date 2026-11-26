"""
[题目编号]: LeetCode 139. 单词拆分 (Word Break)
[难度]: Medium (字符串上的完全背包 / 词典匹配 DP)
[所属专题]: 10_dynamic_programming
[前置知识]: 10_dynamic_programming/01_lc0322_coin_change (完全背包)、set 查询

一、题目描述
给你一个字符串 `s` 和一个字符串列表 `word_dict` 作为词典。请判断是否可以利用词典中的词拼接出 `s`。
注意：词典中的词可以重复使用，且不要求用尽词典。

示例:
- 输入: s = "leetcode", word_dict = ["leet", "code"] -> True
- 输入: s = "applepenapple", word_dict = ["apple", "pen"] -> True
- 输入: s = "catsandog", word_dict = ["cats", "dog", "sand", "and", "cat"] -> False
- 边界: s="" -> True；词典为空且 s 非空 -> False

二、解法对比与复杂度
把「词典里的词」看成「硬币面额」，把「能否拼出字符串 s」看成「能否凑出背包容量」。
这是完全背包在字符串上的版本：每个词可无限次使用。

1. 解法一（记忆化 DFS）:
   - 从当前位置 `start` 出发，枚举词典中每个词，若 `s[start:]` 以此词开头，则递归 `start + len(word)`。
   - 时间复杂度: O(n * m * L)（n 为串长，m 为词典大小，L 为平均词长），有缓存
2. 解法二（一维布尔 DP）:
   - `dp[i] = True` 表示前缀 `s[:i]` 可被拆分。
   - 转移: 若存在 `j < i` 使得 `dp[j]` 为真且 `s[j:i]` 在词典中，则 `dp[i] = True`。
   - 优化: 用 `set` 存词典；只枚举合理词长窗口。
   - 时间复杂度: O(n^2)（或 O(n * max_word_len)）
   - 空间复杂度: O(n)

与 LC 322 的区别：322 求最少硬币数；本题只问「能否拼成」。

三、工程与 AI/大数据实战映射
- 分词 / 关键词词典匹配: 规则分词、敏感词是否可覆盖整段文本、RAG 关键词路由时判断查询能否被领域词典解释。
"""

from __future__ import annotations

from functools import lru_cache


def word_break_memo(s: str, word_dict: list[str]) -> bool:
    """解法一：记忆化 DFS，从 start 位置尝试匹配每个词典词。"""
    words = set(word_dict)

    @lru_cache(maxsize=None)
    def dfs(start: int) -> bool:
        if start == len(s):
            return True
        for word in words:
            end = start + len(word)
            if end <= len(s) and s[start:end] == word and dfs(end):
                return True
        return False

    return dfs(0)


def word_break_dp(s: str, word_dict: list[str]) -> bool:
    """解法二：布尔 DP，dp[i] 表示 s[:i] 能否被拆分。"""
    words = set(word_dict)
    max_len = max((len(word) for word in words), default=0)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # 空前缀可拆

    for i in range(1, n + 1):
        # 只回看「可能的词长」窗口，避免无效切片
        left_bound = max(0, i - max_len)
        for j in range(left_bound, i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[n]


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('leetcode', ['leet', 'code'], True),
        ('applepenapple', ['apple', 'pen'], True),
        ('catsandog', ['cats', 'dog', 'sand', 'and', 'cat'], False),
        ('', ['a'], True),
        ('a', [], False),
        ('aaaaaaa', ['aaaa', 'aaa'], True),
        ('catsandog', ['cats', 'dog', 'sand', 'and', 'cat', 'an'], True),
    ]
    for solver in (word_break_memo, word_break_dp):
        for text, dictionary, expected in cases:
            actual = solver(text, dictionary)
            assert actual is expected, f'{solver.__name__} 失败: {text!r} -> {actual}'
    print('✅ LeetCode 139 (单词拆分) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 139. 单词拆分 {'*' * 12}", sep='', end='\n\n')
    print('leetcode + [leet, code] ->', word_break_dp('leetcode', ['leet', 'code']))
    run_tests()


if __name__ == '__main__':
    bootstrap()
