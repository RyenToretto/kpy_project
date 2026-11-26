# `09_greedy` | 贪心与区间调度专题

- **学习阶段**: 第 3 阶段
- **前置语法**: `sorted(..., key=lambda x: x[0])` 自定义排序
- **为什么学它**: 区间排序 + 贪心合并是后端排班、RAG 重叠文本块合并、大数据分片区间整理的高频套路。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 56. 合并区间 | Medium | 按区间左端点排序后贪心合并 | [00_lc0056_merge_intervals.py](./00_lc0056_merge_intervals.py) | ✅ 已完成 |
| `01_` | LeetCode 55. 跳跃游戏 | Medium | 维护当前能到达的最远下标 | [`01_lc0055_jump_game.py`](./01_lc0055_jump_game.py) | ✅ 已完成 |
| `02_` | LeetCode 53. 最大子数组和 | Medium | Kadane：负贡献丢弃重开，单遍求最大连续和 | [02_lc0053_maximum_subarray.py](./02_lc0053_maximum_subarray.py) | ✅ 已完成 |
| `03_` | LeetCode 45. 跳跃游戏 II | Medium | 贪心分层求最少跳跃次数 | [03_lc0045_jump_game_ii.py](./03_lc0045_jump_game_ii.py) | ✅ 已完成 |
| `04_` | LeetCode 122. 买卖股票的最佳时机 II | Medium | 累加所有上涨段差值（可多次交易） | [04_lc0122_best_time_to_buy_and_sell_stock_ii.py](./04_lc0122_best_time_to_buy_and_sell_stock_ii.py) | ✅ 已完成 |
| `05_` | LeetCode 435. 无重叠区间 | Medium | 按右端点排序，删最少使无重叠（对照 LC 56） | [05_lc0435_non_overlapping_intervals.py](./05_lc0435_non_overlapping_intervals.py) | ✅ 已完成 |
