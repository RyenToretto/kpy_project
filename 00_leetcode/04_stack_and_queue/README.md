# `04_stack_and_queue` | 栈、队列与单调栈专题

- **学习阶段**: 第 2 阶段
- **前置语法**: `list` 的 `.append()` / `.pop()`、`dict` 映射、`collections.deque`
- **为什么学它**: 栈（后进先出 LIFO）解决**最近相关性/括号嵌套/语法解析**；单调栈专门在 `O(n)` 时间内解决「下一个更大/更小元素」。

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 20. 有效的括号 | Easy | 栈 + 右括号到左括号字典映射 | [00_lc0020_valid_parentheses.py](./00_lc0020_valid_parentheses.py) | ✅ 已完成 |
| `01_` | LeetCode 739. 每日温度 | Medium | 单调递减栈存下标 | [01_lc0739_daily_temperatures.py](./01_lc0739_daily_temperatures.py) | ✅ 已完成 |
