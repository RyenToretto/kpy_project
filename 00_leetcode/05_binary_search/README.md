# `05_binary_search` | 二分查找专题

- **学习阶段**: 第 2 阶段
- **前置语法**: 有序列表、整数除法 `//`、`while left <= right`
- **为什么学它**: 二分查找不仅能把有序查找从 `O(n)` 加速到 `O(log n)`（10 亿条数据只需 ~30 次比较），更可以拓展到「旋转数组」「答案单调二分」。

## 二分防死循环核心（左闭右闭区间 `[left, right]`）
- `left, right = 0, len(nums) - 1`
- `while left <= right:`
- `mid = left + (right - left) // 2`
- 缩区间时明确 `+1` 或 `-1`：`left = mid + 1` / `right = mid - 1`

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 704. 二分查找 | Easy | 标准左闭右闭区间二分 + `bisect` 对照 | [00_lc0704_binary_search.py](./00_lc0704_binary_search.py) | ✅ 已完成 |
| `01_` | LeetCode 33. 搜索旋转排序数组 | Medium | 判断哪一半有序再舍弃一半 | [01_lc0033_search_in_rotated_sorted_array.py](./01_lc0033_search_in_rotated_sorted_array.py) | ✅ 已完成 |
