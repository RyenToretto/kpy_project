# `06_linked_list` | 链表与缓存结构专题

- **学习阶段**: 第 3 阶段
- **前置语法**: Python 类与对象 `class ListNode`、引用赋值、哨兵节点（Dummy Node）、双向链表 + 哈希表
- **为什么学它**: 理解「对象引用」如何串联数据，以及 `哈希表 + 双向链表` 如何组合出 `O(1)` 读写的 **LRU 缓存**（大厂系统设计高频题）。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 206. 反转链表 | Easy | 迭代三指针 vs 递归反转 | [00_lc0206_reverse_linked_list.py](./00_lc0206_reverse_linked_list.py) | ✅ 已完成 |
| `01_` | LeetCode 146. LRU 缓存 | Medium | 手写双向链表+哈希 vs `OrderedDict` | [01_lc0146_lru_cache.py](./01_lc0146_lru_cache.py) | ✅ 已完成 |
| `02_` | LeetCode 23. 合并 K 个升序链表 | Hard | 小顶堆多路归并 `O(N log k)` vs 分治两两归并 | [02_lc0023_merge_k_sorted_lists.py](./02_lc0023_merge_k_sorted_lists.py) | ✅ 已完成 |
| `03_` | LeetCode 460. LFU 缓存 | Hard | 双哈希 + 频率桶 `OrderedDict` 实现 `O(1)` 淘汰 | [03_lc0460_lfu_cache.py](./03_lc0460_lfu_cache.py) | ✅ 已完成 |
| `04_` | LeetCode 142. 环形链表 II | Medium | Floyd 快慢指针判环（覆盖 141）+ 同速相遇定入环口 | [04_lc0142_linked_list_cycle_ii.py](./04_lc0142_linked_list_cycle_ii.py) | ✅ 已完成 |
| `05_` | LeetCode 19. 删除链表的倒数第 N 个结点 | Medium | 快慢指针间距 + 哨兵节点一次扫描 | [05_lc0019_remove_nth_from_end.py](./05_lc0019_remove_nth_from_end.py) | ✅ 已完成 |
| `06_` | LeetCode 21. 合并两个有序链表 | Easy | 哨兵双指针归并（LC 23 的积木） | [06_lc0021_merge_two_sorted_lists.py](./06_lc0021_merge_two_sorted_lists.py) | ✅ 已完成 |
