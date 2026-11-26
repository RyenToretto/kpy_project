# `10_dynamic_programming` | 动态规划专题

- **学习阶段**: 第 4 阶段（从入门一维 DP 到二维字符串 DP）
- **前置语法**: 递归与 `@lru_cache` 记忆化、一维/二维列表初始化 `[[0] * m for _ in range(n)]`
- **为什么学它**: 动态规划（DP）不是背公式，而是**「大问题拆成小问题 + 把算过的子问题结果存起来避免重复算」**。沿着「记忆化递归 -> 填表 DP -> 状态压缩」三步学，小白也能稳稳拿下！

## 顺序刷题清单（从 `00_` 开始，Easy -> Medium -> Hard 经典）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 70. 爬楼梯 | Easy | 记忆化搜索 -> DP 数组 -> O(1) 滚动变量 | [00_lc0070_climbing_stairs.py](./00_lc0070_climbing_stairs.py) | ✅ 已完成 |
| `01_` | LeetCode 322. 零钱兑换 | Medium | 完全背包模型 `dp[x] = min(dp[x], dp[x-coin]+1)` | [01_lc0322_coin_change.py](./01_lc0322_coin_change.py) | ✅ 已完成 |
| `02_` | LeetCode 72. 编辑距离 | Medium/Hard | 二维字符串 DP + 滚动数组 `O(min(m,n))` 空间压缩 | [02_lc0072_edit_distance.py](./02_lc0072_edit_distance.py) | ✅ 已完成 |
| `03_` | LeetCode 300. 最长递增子序列 (LIS) | Medium | `O(n^2)` DP vs `bisect_left` 贪心二分 `O(n log n)` | [03_lc0300_longest_increasing_subsequence.py](./03_lc0300_longest_increasing_subsequence.py) | ✅ 已完成 |
