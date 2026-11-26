# `10_dynamic_programming` | 动态规划专题

- **学习阶段**: 第 4 阶段（从入门一维 DP 到二维字符串 DP）
- **前置语法**: 递归与 `@lru_cache` 记忆化、一维/二维列表初始化 `[[0] * m for _ in range(n)]`
- **为什么学它**: 动态规划（DP）不是背公式，而是**「大问题拆成小问题 + 把算过的子问题结果存起来避免重复算」**。沿着「记忆化递归 -> 填表 DP -> 状态压缩」三步学，小白也能稳稳拿下！

## 动规五部曲 & 背包遍历顺序速记（参考《代码随想录》思维框架）
每次拆解 DP 固定问自己这 5 步：
1. **确定 `dp` 下标与值的含义**；2. **推导状态转移方程**；3. **思考 `dp` 怎么初始化**；4. **确定遍历顺序**（最容易写反！）；5. **举例手算 / 打印 `dp` 数组排错**。

| 背包类型 | 一维 `dp` 内层容量遍历顺序 | 代表题 | 核心原因 |
| --- | --- | --- | --- |
| **0-1 背包**（每件物品最多选 1 次） | **外层物品，内层倒序容量** | `04_lc0416` 分割等和子集 | 保证 `dp[s - num]` 读取的是上一轮还没放入该物品的旧状态 |
| **完全背包**（每件物品可无限选） | **正序容量** | `01_lc0322` 零钱兑换 | 允许本轮刚更新完的 `dp[x - coin]` 继续累加同一枚硬币 |

## 顺序刷题清单（从 `00_` 开始，Easy -> Medium -> Hard 经典）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 70. 爬楼梯 | Easy | 记忆化搜索 -> DP 数组 -> O(1) 滚动变量 | [00_lc0070_climbing_stairs.py](./00_lc0070_climbing_stairs.py) | ✅ 已完成 |
| `01_` | LeetCode 322. 零钱兑换 | Medium | 完全背包模型 `dp[x] = min(dp[x], dp[x-coin]+1)`（正序） | [01_lc0322_coin_change.py](./01_lc0322_coin_change.py) | ✅ 已完成 |
| `02_` | LeetCode 72. 编辑距离 | Medium/Hard | 二维字符串 DP + 滚动数组 `O(min(m,n))` 空间压缩 | [02_lc0072_edit_distance.py](./02_lc0072_edit_distance.py) | ✅ 已完成 |
| `03_` | LeetCode 300. 最长递增子序列 (LIS) | Medium | `O(n^2)` DP vs `bisect_left` 贪心二分 `O(n log n)` | [03_lc0300_longest_increasing_subsequence.py](./03_lc0300_longest_increasing_subsequence.py) | ✅ 已完成 |
| `04_` | LeetCode 416. 分割等和子集 | Medium | 0-1 背包一维滚动数组（内层容量**倒序**遍历防重复选） | [04_lc0416_partition_equal_subset_sum.py](./04_lc0416_partition_equal_subset_sum.py) | ✅ 已完成 |
| `05_` | LeetCode 198. 打家劫舍 | Medium | 相邻互斥一维 DP：`max(不偷, 偷+隔一间)`，可滚动到 O(1) 空间 | [05_lc0198_house_robber.py](./05_lc0198_house_robber.py) | ✅ 已完成 |
| `06_` | LeetCode 139. 单词拆分 | Medium | 字符串完全背包：`dp[i]` 前缀能否被词典拼接 | [06_lc0139_word_break.py](./06_lc0139_word_break.py) | ✅ 已完成 |
