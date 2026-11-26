# `01_array_and_hashing` | 数组与哈希表专题

- **学习阶段**: 第 1 阶段（核心基石，面试最高频）
- **前置语法**: `list`、`dict`（字典）、`set`（集合）、`for`、`enumerate()`、`collections.Counter` / `defaultdict`
- **为什么学它**: 80% 的初级和中级算法优化，本质都是**「用空间换时间」**——把原本嵌套循环 $O(n^2)$ 的查找，借助哈希表（Python 的 `dict` / `set`）降维到 $O(n)$。

## 核心心法（先背会这 3 行）
1. **判存在 / 去重**: 用 `set`（`x in seen` 平均 `O(1)`）。
2. **找配对 / 记下标**: 用 `dict`（`seen[val] = idx`）。
3. **统计频次 / 分组**: 用 `Counter(items)` 或 `defaultdict(list)`。

## 顺序刷题清单（从 `00_` 开始，Easy -> Medium）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 1. 两数之和 | Easy | 哈希表找补数 `target - num` | [00_lc0001_two_sum.py](./00_lc0001_two_sum.py) | ✅ 已完成 |
| `01_` | LeetCode 217. 存在重复元素 | Easy | `set` 集合去重与提前退出 | [01_lc0217_contains_duplicate.py](./01_lc0217_contains_duplicate.py) | ✅ 已完成 |
| `02_` | LeetCode 242. 有效的字母异位词 | Easy | 排序 vs 频次统计 `Counter` | [02_lc0242_valid_anagram.py](./02_lc0242_valid_anagram.py) | ✅ 已完成 |
| `03_` | LeetCode 49. 字母异位词分组 | Medium | `defaultdict(list)` + `tuple` 签名键 | [03_lc0049_group_anagrams.py](./03_lc0049_group_anagrams.py) | ✅ 已完成 |
| `04_` | LeetCode 347. 前 K 个高频元素 | Medium | 最小堆 `O(n log k)` vs 桶排序 `O(n)` | [04_lc0347_top_k_frequent_elements.py](./04_lc0347_top_k_frequent_elements.py) | ✅ 已完成 |
| `05_` | LeetCode 128. 最长连续序列 | Medium | 集合去重 + 只从序列起点向后扩展 | [05_lc0128_longest_consecutive_sequence.py](./05_lc0128_longest_consecutive_sequence.py) | ✅ 已完成 |
