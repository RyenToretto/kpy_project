# `02_two_pointers` | 双指针专题

- **学习阶段**: 第 2 阶段
- **前置语法**: `01_array_and_hashing`、列表下标交换 `a, b = b, a`、`while left < right`
- **为什么学它**: 双指针是把嵌套循环 `O(n^2)` 压缩为 `O(n)`、同时把空间复杂度从 `O(n)` 压到 `O(1)` 原地操作的经典利器。

## 核心心法
1. **快慢指针（同向）**: `fast` 负责探路，`slow` 负责写有效数据（去重/移动零）。
2. **相向双指针（左右夹逼）**: `left = 0, right = n - 1`，根据条件决定是 `left += 1` 还是 `right -= 1`。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 283. 移动零 | Easy | 同向快慢指针原地交换 | [00_lc0283_move_zeroes.py](./00_lc0283_move_zeroes.py) | ✅ 已完成 |
| `01_` | LeetCode 125. 验证回文串 | Easy | 左右双指针 + `isalnum()` 跳过符号 | [01_lc0125_valid_palindrome.py](./01_lc0125_valid_palindrome.py) | ✅ 已完成 |
| `02_` | LeetCode 15. 三数之和 | Medium | 排序 + 固定一位 + 左右双指针 + 三重去重 | [02_lc0015_three_sum.py](./02_lc0015_three_sum.py) | ✅ 已完成 |
| `03_` | LeetCode 11. 盛最多水的容器 | Medium | 左右双指针贪心收缩短板 | 可用 `py-study-generator` 按需生成 | 📝 待生成 |
