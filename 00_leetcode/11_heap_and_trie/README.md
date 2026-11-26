# `11_heap_and_trie` | 堆（优先队列）与前缀树专题

- **学习阶段**: 第 4 阶段
- **前置语法**: `heapq` 标准库、`dict` 树状嵌套
- **为什么学它**:
  - **堆 (`heapq`)**: 大数据流式 Top-K 筛选的标配武器，内存只需 `O(k)` 而不是全量排序 `O(n)`。
  - **前缀树 (Trie)**: 搜索引擎自动补全、敏感词过滤、分词词典 (Tokenizer) 的核心底层结构。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 215. 数组中的第K个最大元素 | Medium | 容量为 k 的小顶堆 vs 三路快选 | [00_lc0215_kth_largest_element.py](./00_lc0215_kth_largest_element.py) | ✅ 已完成 |
| `01_` | LeetCode 208. 实现 Trie (前缀树) | Medium | 字典树节点 `children: dict` + `is_end` | [01_lc0208_implement_trie.py](./01_lc0208_implement_trie.py) | ✅ 已完成 |
