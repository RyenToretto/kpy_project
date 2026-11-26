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
1. 解法一（二维 DP 表格 - 最直观易懂）:
   - 思路: 把两个字符串的匹配过程画成一张 (m+1) x (n+1) 的表。
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
   - 空间复杂度: O(m * n)
2. 解法二（一维滚动数组空间压缩 - 工程内存最优版）:
   - 思路: 仔细看转移方程，计算第 `i` 行时只用到「上一行 `i-1`」和「当前行左边 `j-1`」。因此只需一个一维数组 `dp[0..n]`！唯一细节是：更新 `dp[j]` 前，先用 `prev_diag` 保存它原来的旧值（即左上角 `dp[i-1][j-1]`）。再把较短的字符串放到内层循环，空间就能压到 `O(min(m, n))`。
   - 时间复杂度: O(m * n)
   - 空间复杂度: O(min(m, n))

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


def min_distance_rolling(word1: str, word2: str) -> int:
    """解法二：一维滚动数组空间压缩，空间复杂度降到 O(min(m, n))。"""
    # 让较短的字符串作为列（dp 数组长度），进一步压低内存占用
    if len(word1) < len(word2):
        word1, word2 = word2, word1

    m, n = len(word1), len(word2)
    dp = list(range(n + 1))  # 初始对应第 0 行：把空串变成 word2[:j] 需要 j 次插入

    for i in range(1, m + 1):
        prev_diag = dp[0]  # 记录旧的左上角 dp[i-1][0]
        dp[0] = i  # 新一行的第 0 列：删掉前 i 个字符需要 i 步
        for j in range(1, n + 1):
            old_top = dp[j]  # 先缓存 dp[i-1][j]，它将在下一列成为左上角
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev_diag
            else:
                dp[j] = 1 + min(
                    old_top,    # 删除 word1[i-1]（来自正上方）
                    dp[j - 1],  # 插入 word2[j-1]（来自正左方）
                    prev_diag,  # 替换（来自左上角）
                )
            prev_diag = old_top

    return dp[n]


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('horse', 'ros', 3),
        ('intention', 'execution', 5),
        ('', 'abc', 3),
        ('abc', '', 3),
        ('abc', 'abc', 0),
        ('abcdef', 'azced', 3),
    ]
    for solver in (min_distance, min_distance_rolling):
        for w1, w2, expected in cases:
            assert solver(w1, w2) == expected, f'{solver.__name__} 失败: {w1!r} -> {w2!r}'
    print('✅ LeetCode 72 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 72. 编辑距离 {'*' * 12}", sep='', end='\n\n')
    print(f'"horse" -> "ros" 最少编辑步数: {min_distance("horse", "ros")}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
