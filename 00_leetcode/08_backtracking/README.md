# `08_backtracking` | 回溯与递归搜索专题

- **学习阶段**: 第 3 阶段
- **前置语法**: 递归函数、列表 `.copy()`（防止引用共享坑！）、`used` 布尔标记数组
- **为什么学它**: 面对「穷举所有排列/组合/子集/合法方案」问题，回溯就是标准的「选一个 -> 递归深挖 -> 撤销选择恢复现场」三步曲。

## 回溯三部曲与「树层去重」心法（参考《代码随想录》）
1. **函数参数与返回值**：一般无返回值（`None`），靠外部 `results` 收集满足条件的 `path.copy()`。
2. **终止条件**：收集到叶子节点或 `remaining == 0` 时存档返回。
3. **单层搜索循环 + 去重核心**：
   - 有重复数字且结果不能重复时：**先排序**，再写 `if i > start and nums[i] == nums[i - 1]: continue`；
   - 它只跳过**同一树层**（横向换起点时遇到相同数字），不会误杀**同一树枝**（纵向往下选第二张相同面值卡片）。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 46. 全排列 | Medium | `path` + `used` 标记 + `path.copy()` 快照 | [00_lc0046_permutations.py](./00_lc0046_permutations.py) | ✅ 已完成 |
| `01_` | LeetCode 78. 子集 | Medium | 选与不选 / `start_index` 去重 | [01_lc0078_subsets.py](./01_lc0078_subsets.py) | ✅ 已完成 |
| `02_` | LeetCode 51. N 皇后 | Hard | 按行回溯 + 列/斜线集合剪枝 | [02_lc0051_n_queens.py](./02_lc0051_n_queens.py) | ✅ 已完成 |
| `03_` | LeetCode 40. 组合总和 II | Medium | 先排序剪枝 + 树层去重 (`i > start and val == prev`) | [03_lc0040_combination_sum_ii.py](./03_lc0040_combination_sum_ii.py) | ✅ 已完成 |
| `04_` | LeetCode 39. 组合总和 | Medium | 可无限次选用同一数字（递归传 `i`，对照 LC 40） | [04_lc0039_combination_sum.py](./04_lc0039_combination_sum.py) | ✅ 已完成 |
