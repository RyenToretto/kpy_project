"""
[题目编号]: LeetCode 127. 单词接龙 (Word Ladder)
[难度]: Hard (隐式图最短路 / BFS 层序)
[所属专题]: 12_graph
[前置知识]: 12_graph/01_lc0200_number_of_islands、collections.deque

一、题目描述
字典 `word_list` 中从 `begin_word` 到 `end_word` 的转换序列，每次只改一个字母，且中间词必须在词典中。
返回最短转换序列的长度；无法转换则返回 0。（长度含起点）

示例:
- begin="hit", end="cog", list=["hot","dot","dog","lot","log","cog"] -> 5 (hit->hot->dot->dog->cog)
- 同上但无 "cog" -> 0

二、解法
把每个词看成图节点，只差一个字母的词之间有边；BFS 求最短路径。
优化: 用通用状态 `h*t` 建桶，避免两两比较 O(n^2 * L)。
时间约 O(n * L^2)，空间 O(n * L)。

三、工程映射
- 编辑距离为 1 的最短改写链: 拼写纠错建议路径、配置状态最短迁移步骤。
"""

from __future__ import annotations

from collections import defaultdict, deque


def ladder_length(begin_word: str, end_word: str, word_list: list[str]) -> int:
    """BFS 最短转换长度；用通配桶加速邻居查找。"""
    words = set(word_list)
    if end_word not in words:
        return 0

    buckets: dict[str, list[str]] = defaultdict(list)
    word_len = len(begin_word)
    for word in words:
        for i in range(word_len):
            buckets[word[:i] + '*' + word[i + 1:]].append(word)

    queue: deque[tuple[str, int]] = deque([(begin_word, 1)])
    visited = {begin_word}

    while queue:
        word, steps = queue.popleft()
        if word == end_word:
            return steps
        for i in range(word_len):
            pattern = word[:i] + '*' + word[i + 1:]
            for nxt in buckets.get(pattern, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, steps + 1))
            buckets[pattern] = []  # 该桶已扩展过，清空避免重复
    return 0


def run_tests() -> None:
    assert ladder_length('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog']) == 5
    assert ladder_length('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log']) == 0
    assert ladder_length('a', 'c', ['a', 'b', 'c']) == 2
    assert ladder_length('hot', 'dog', ['hot', 'dog']) == 0
    print('✅ LeetCode 127 (单词接龙 BFS) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 127. 单词接龙 {'*' * 12}", sep='', end='\n\n')
    print(ladder_length('hit', 'cog', ['hot', 'dot', 'dog', 'lot', 'log', 'cog']))
    run_tests()


if __name__ == '__main__':
    bootstrap()
