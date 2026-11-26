"""
[题目编号]: LeetCode 72. 编辑距离 (Edit Distance / Levenshtein Distance)
[难度]: Medium / 经典 Hard 门槛（NLP 与大模型评测核心算法）
[所属专题]: 10_dynamic_programming
[前置知识]: 二维列表 `[[0] * n for _ in range(m)]`、字符串索引

一、题目描述
给你两个单词 `word1` 和 `word2`，请返回将 `word1` 转换成 `word2` 所使用的最少操作数。
你可以对一个单词进行如下三种操作（每次算 1 步）：
1. 插入一个字符
2. 删除一个字符
3. 替换一个字符

示例:
- 输入: word1 = "horse", word2 = "ros" -> 输出: 3 (horse -> rorse -> rose -> ros)
- 输入: word1 = "intention", word2 = "execution" -> 输出: 5
- 边界: ("", "abc") -> 3；("abc", "abc") -> 0

二、解法与复杂度
- 思路（二维 DP 表格：把两个字符串的匹配过程画成一张 (m+1) x (n+1) 的表）:
  - 状态定义: `dp[i][j]` 表示把 `word1[:i]`（前 `i` 个字符）变成 `word2[:j]`（前 `j` 个字符）的最少步数。
  - 初始化第 0 行与第 0 列:
    - `dp[i][0] = i`（把长度为 i 的串删空需要 i 步）
    - `dp[0][j] = j`（把空串插入 j 个字符需要 j 步）
  - 状态转移（比较 `word1[i - 1]` 和 `word2[j - 1]`）:
    - 若两个字符相等：这一步不用改！`dp[i][j] = dp[i - 1][j - 1]`
    - 若不相等：三种操作里挑步数最少的 + 1：
      - 删除 `word1[i-1]`: `dp[i - 1][j] + 1`
      - 在 `word1` 插入 `word2[j-1]`: `dp[i][j - 1] + 1`
      - 把 `word1[i-1]` 替换为 `word2[j-1]`: `dp[i - 1][j - 1] + 1`
- 时间复杂度: O(m * n)
- 空间复杂度: O(m * n)（还可压缩到 O(min(m, n))，二维版最易读懂）

三、工程与 AI/大数据实战映射
- 大数据清洗与实体对齐: 模糊匹配公司名/地址/人名拼写错误（Fuzzy Match）。
- 大模型 / ASR / OCR 评测: 语音识别字错率 (WER/CER)、OCR 识别准确率、RAG 幻觉/字符串微调差异比对，底层核心就是编辑距离！
"""

from __future__ import annotations


def min_distance(word1: str, word2: str) -> int:
    """二维 DP 计算 Levenshtein 编辑距离。"""
    m, n = len(word1), len(word2)
    # 注意：千万不要写成 [[0] * (n + 1)] * (m + 1)，那样所有行会共享同一份列表内存！
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # 删除
                    dp[i][j - 1],      # 插入
                    dp[i - 1][j - 1],  # 替换
                )

    return dp[m][n]


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('horse', 'ros', 3),
        ('intention', 'execution', 5),
        ('', 'abc', 3),
        ('abc', '', 3),
        ('abc', 'abc', 0),
    ]
    for w1, w2, expected in cases:
        assert min_distance(w1, w2) == expected, f'失败: {w1!r} -> {w2!r}'
    print('✅ LeetCode 72 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 72. 编辑距离 {'*' * 12}", sep='', end='\n\n')
    print(f'"horse" -> "ros" 最少编辑步数: {min_distance("horse", "ros")}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
