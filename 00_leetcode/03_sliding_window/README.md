# `03_sliding_window` | 滑动窗口专题

- **学习阶段**: 第 2 阶段（覆盖 Easy -> Medium -> Hard 经典模板）
- **前置语法**: `02_two_pointers`、`dict` / `set`、`Counter`
- **为什么学它**: 滑动窗口本质是**满足单调性的同向双指针 `[left, right]`**，用于高效解决「连续子数组 / 连续子串」的最值问题。

## 变长滑窗万能 4 步模板
1. `right` 向右扩张，把新元素纳入窗口状态；
2. 判断当前窗口是否「不合法」或「已满足条件」；
3. 按需收缩 `left += 1` 直到恢复条件（或尽可能缩短窗口）；
4. 更新最优答案 `best`。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 121. 买卖股票的最佳时机 | Easy | 一次遍历维护历史最低买入价 | [00_lc0121_best_time_to_buy_and_sell_stock.py](./00_lc0121_best_time_to_buy_and_sell_stock.py) | ✅ 已完成 |
| `01_` | LeetCode 3. 无重复字符的最长子串 | Medium | 变长滑窗 + 记录字符最近下标 | [01_lc0003_longest_substring_without_repeating.py](./01_lc0003_longest_substring_without_repeating.py) | ✅ 已完成 |
| `02_` | LeetCode 76. 最小覆盖子串 | Hard | `need` 与 `window` 双频次计数滑窗模板 | [02_lc0076_minimum_window_substring.py](./02_lc0076_minimum_window_substring.py) | ✅ 已完成 |
