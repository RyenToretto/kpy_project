"""
[题目编号]: LeetCode 208. 实现 Trie (前缀树 / 字典树)
[难度]: Medium
[所属专题]: 11_heap_and_trie
[前置知识]: class、dict 嵌套树结构

一、题目描述
请你实现一个 `Trie`（前缀树），支持三个核心操作：
- `insert(word)`: 向前缀树中插入字符串 `word`；
- `search(word)`: 如果完整的单词 `word` 在前缀树中，返回 `True`，否则 `False`；
- `starts_with(prefix)`: 如果之前插入的字符串中存在以 `prefix` 为前缀的，返回 `True`，否则 `False`。

示例:
- insert("apple") -> search("apple") == True -> search("app") == False -> starts_with("app") == True -> insert("app") -> search("app") == True

二、解法与复杂度
- 思路: 每个节点 `TrieNode` 包含两样东西：
  1) `children: dict[str, TrieNode]` —— 当前字母通往下一层节点的分支；
  2) `is_end: bool` —— 是否有单词恰好在这里结束！（区分 `"app"` 是前缀还是一个独立插入过的完整单词）。
- 时间复杂度: 插入/查询均 O(L)，L 为单词长度，与词库总规模无关！
- 空间复杂度: O(总字符数)

三、工程与 AI/大数据实战映射
- 搜索框自动补全 (Autocomplete) & 大模型词表/敏感词过滤: 当后台有 100 万个热词或违禁词时，不用逐个正则扫描，一棵前缀树只需 O(文本长度) 就能扫完敏感词或提示联想词！
"""

from __future__ import annotations


class _TrieNode:
    """前缀树节点：记录子节点映射和单词结尾标记。"""

    def __init__(self) -> None:
        self.children: dict[str, _TrieNode] = {}
        self.is_end = False


class Trie:
    """字典树 (Prefix Tree) 实现。"""

    def __init__(self) -> None:
        self.root = _TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = _TrieNode()
            node = node.children[ch]
        node.is_end = True

    def _find_node(self, prefix: str) -> _TrieNode | None:
        """公共前缀查找辅助方法，避免 search 和 starts_with 代码重复。"""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None


def run_tests() -> None:
    """自动化断言测试。"""
    trie = Trie()
    trie.insert('apple')
    assert trie.search('apple') is True
    assert trie.search('app') is False
    assert trie.starts_with('app') is True
    trie.insert('app')
    assert trie.search('app') is True
    assert trie.starts_with('xyz') is False
    print('✅ LeetCode 208 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 208. 实现 Trie (前缀树) {'*' * 12}", sep='', end='\n\n')
    trie = Trie()
    for word in ('agent', 'rag', 'rank'):
        trie.insert(word)
    print(f'查询完整词 "ra": {trie.search("ra")}, 前缀 "ra": {trie.starts_with("ra")}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
