# `00_leetcode` | 从零到精通 Python 算法训练营（Easy -> Medium -> Hard）

**总题数：41**（已完成 35，待生成 6；15 个专题，`00_` 到 `14_`）

欢迎来到 `00_leetcode`！这套目录专为**小白从零系统刷题、打通 Python 工程底层、并服务大数据 / 数据分析 / RAG / AI Agent / 全栈开发与求职面试**而设计。

## 为什么这套路线适合你？
1. **和当前 `chapter01`~`chapter05` 无缝衔接**：第 `00_` 专题只需 `if / for / while / % / 字符串切片`，写完立刻有成就感。
2. **所有目录和题目均从 `00_` 顺序编号**：不用纠结先刷哪道，从 `00_warmup_basics/00_lc1480_running_sum.py` 开始一路往后学。
3. **每道题包含多版本对比 + 大白话逐行注释 + AI/大数据实战映射 + 自动 `assert` 测试**：在 PyCharm 点绿色运行按钮即可同时看到示例输出与测试结果。
4. **可随时按需扩题**：直接对 AI 说「用 `py-study-generator` 生成 `00_leetcode/02_two_pointers/` 的下一题」，即可按同一规范自动生成。

## 一、刷题前必背的 Python 算法内置工具速查
学完 `chapter05_match` 后，建议同步掌握以下 6 个高频内置能力（在各专题代码中都有示范）：
- `dict`（哈希表）：`O(1)` 均摊查重与计数（大数据清洗、RAG 文档去重基础）
- `set`（集合）：去重与 `O(1)` 成员判断 `x in seen`
- `enumerate(nums)`：同时拿到下标 `i` 和元素 `val`
- `collections.Counter` / `defaultdict`：统计词频、分组聚合（等同 SQL `GROUP BY`）
- `collections.deque`：双端队列 `O(1)` 出队，BFS 层序遍历与滑窗必备
- `heapq`：小顶堆，做流式 Top-K、中位数与检索重排（Rerank）必考

## 二、顺序学习地图（`00_` -> `14_`，由易到难）

| 序号 | 专题目录 | 难度梯度 | 核心能力 | 对应真实工程 / AI / 大数据场景 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | [00_warmup_basics](./00_warmup_basics/README.md) | Easy | 循环、取余、前缀累加、回文 | 指标累计（GMV/DAU 累加）、基础数据清洗 | ✅ 已就绪 (4题) |
| `01_` | [01_array_and_hashing](./01_array_and_hashing/README.md) | Easy -> Medium | 哈希查找、频次统计、桶/集合去重 | 日志去重、词频统计、RAG Top-K 召回 | ✅ 已就绪 (6题) |
| `02_` | [02_two_pointers](./02_two_pointers/README.md) | Easy -> Medium | 快慢指针、左右夹逼、排序去重 | 内存原地清洗、有序表双路归并 | ✅ 已完成 3 / 📝 待生成 1 |
| `03_` | [03_sliding_window](./03_sliding_window/README.md) | Easy -> Hard | 单调收益、变长窗口、最小覆盖模板 | 时序指标滑窗、Token/上下文窗口切分 | ✅ 已就绪 (3题) |
| `04_` | [04_stack_and_queue](./04_stack_and_queue/README.md) | Easy -> Medium | 栈括号匹配、单调栈 | JSON/代码括号解析、LLM 工具调用参数校验 | ✅ 已就绪 (2题) |
| `05_` | [05_binary_search](./05_binary_search/README.md) | Easy -> Medium | 标准二分边界、旋转数组二分 | 倒排索引查找、有序分片定位 | ✅ 已就绪 (2题) |
| `06_` | [06_linked_list](./06_linked_list/README.md) | Easy -> Medium | 指针重连、双向链表 + 哈希 | **LRU 缓存 / 大模型 KV & Prompt 缓存** | ✅ 已就绪 (2题) |
| `07_` | [07_binary_tree](./07_binary_tree/README.md) | Easy -> Medium | 递归 DFS、层序 BFS、`deque` | 文档解析树（HTML/AST）、多步树状推理 | ✅ 已就绪 (2题) |
| `08_` | [08_backtracking](./08_backtracking/README.md) | Medium | 递归路径、撤销选择、剪枝 | 组合配置搜索、Agent 动作规划回退 | ✅ 已完成 1 / 📝 待生成 2 |
| `09_` | [09_greedy](./09_greedy/README.md) | Medium | 排序 + 区间合并 | 调度时间窗合并、RAG 文本片段区间融合 | ✅ 已完成 1 / 📝 待生成 1 |
| `10_` | [10_dynamic_programming](./10_dynamic_programming/README.md) | Easy -> Hard | 记忆化搜索、背包、编辑距离 | **NLP 文本相似度、拼写纠错与评测指标** | ✅ 已就绪 (3题) |
| `11_` | [11_heap_and_trie](./11_heap_and_trie/README.md) | Medium | 最小堆 Top-K、字典树 Trie | **海量数据 Top-K、搜索补全/分词词典** | ✅ 已就绪 (2题) |
| `12_` | [12_graph](./12_graph/README.md) | Medium | 邻接表、Kahn 拓扑排序 | **LangGraph / Airflow / Agent DAG 编排** | ✅ 已完成 1 / 📝 待生成 1 |
| `13_` | [13_bit_and_math](./13_bit_and_math/README.md) | Easy | 异或去偶、位运算压缩 | 布隆过滤器、位图去重、状态压缩 | ✅ 已完成 1 / 📝 待生成 1 |
| `14_` | [14_hard_capstones](./14_hard_capstones/README.md) | Hard | 综合双指针/单调栈/双堆数据流 | **实时数据流中位数**、高难度大厂压轴题 | ✅ 已就绪 (2题) |
| 合计 | 15 个专题 | Easy -> Hard | — | — | **总题数 41**（已完成 35，待生成 6） |

## 三、一键验证全部题解
在项目根目录运行下面命令，可一次验证 `00_leetcode` 下的全部 Python 脚本：

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 00_leetcode
```
