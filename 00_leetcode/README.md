# `00_leetcode` | 从零到精通 Python 算法训练营（Easy -> Medium -> Hard）

**总题数：61**（已完成 61，待生成 0；15 个专题，`00_` 到 `14_`）

欢迎来到 `00_leetcode`！这套目录专为**小白从零系统刷题、打通 Python 工程底层、并服务大数据 / 数据分析 / RAG / AI Agent / 全栈开发与求职面试**而设计。

## 为什么这套路线适合你？
1. **和当前 `00_basic/chapter01`~`00_basic/chapter05` 无缝衔接**：第 `00_` 专题只需 `if / for / while / % / 字符串切片`，写完立刻有成就感。
2. **所有目录和题目均从 `00_` 顺序编号**：不用纠结先刷哪道，从 `00_warmup_basics/00_lc1480_running_sum.py` 开始一路往后学。
3. **每道题包含多版本对比 + 大白话逐行注释 + AI/大数据实战映射 + 自动 `assert` 测试**：在 PyCharm 点绿色运行按钮即可同时看到示例输出与测试结果。
4. **可随时按需扩题**：直接对 AI 说「用 `py-study-generator` 生成 `00_leetcode/02_two_pointers/` 的下一题」，即可按同一规范自动生成。

## 一、刷题前必背的 Python 算法内置工具速查
学完 `00_basic/chapter05_match` 后，建议同步掌握以下 6 个高频内置能力（在各专题代码中都有示范）：
- `dict`（哈希表）：`O(1)` 均摊查重与计数（大数据清洗、RAG 文档去重基础）
- `set`（集合）：去重与 `O(1)` 成员判断 `x in seen`
- `enumerate(nums)`：同时拿到下标 `i` 和元素 `val`
- `collections.Counter` / `defaultdict`：统计词频、分组聚合（等同 SQL `GROUP BY`）
- `collections.deque`：双端队列 `O(1)` 出队，BFS 层序遍历与单调队列滑窗必备
- `heapq`：小顶堆，做流式 Top-K、多路归并、Dijkstra 最短路与检索重排必考

## 二、看数据规模选算法速查表（Python 版）
刷题或处理工程数据时，**先看输入规模 `n`** 就能立刻排除必然超时的方案（Python 约每秒稳定执行 $10^6 \sim 10^7$ 次基本操作，参考 `kamyu104/LeetCode-Solutions` 的 `REFERENCE.md` 并针对 Python 性能调优）：

| 输入规模 `n` | 允许时间复杂度上限 | 常见对应算法与数据结构 |
| --- | --- | --- |
| `n <= 10` | `O(n!)` | 全排列、N 皇后、暴力回溯搜索 |
| `n <= 20` | `O(2^n)` 或 `O(n * 2^n)` | 子集枚举、回溯剪枝、状态压缩 DP |
| `n <= 300 ~ 500` | `O(n^3)` | 区间 DP、Floyd 全源最短路、三重枚举 |
| `n <= 2000 ~ 5000` | `O(n^2)` | 冒泡/选择、二维字符串 DP（编辑距离）、常规两层对比 |
| `n <= 10^5 ~ 10^6` | `O(n log n)` / `O(n)` | 排序、二分/答案二分、堆、树状数组 BIT、单调栈/队列、双指针、滑窗、哈希、KMP、并查集 |
| `n >= 10^8` | `O(log n)` / `O(1)` | 二分查找、数学推导、位运算、前缀公式 |

## 三、顺序学习地图（`00_` -> `14_`，由易到难）

| 序号 | 专题目录 | 难度梯度 | 核心能力 | 对应真实工程 / AI / 大数据场景 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | [00_warmup_basics](./00_warmup_basics/README.md) | Easy | 循环、取余、前缀累加、回文 | 指标累计（GMV/DAU 累加）、基础数据清洗 | ✅ 已就绪 (4题) |
| `01_` | [01_array_and_hashing](./01_array_and_hashing/README.md) | Easy -> Medium | 哈希查找、频次统计、桶去重、前缀和+哈希 | 日志去重、词频统计、区间净增量统计、RAG Top-K 召回 | ✅ 已就绪 (7题) |
| `02_` | [02_two_pointers](./02_two_pointers/README.md) | Easy -> Medium | 快慢指针、左右夹逼、去重、KMP 字符串匹配 | 内存原地清洗、有序表双路归并、敏感词流式匹配 | ✅ 已就绪 (5题) |
| `03_` | [03_sliding_window](./03_sliding_window/README.md) | Easy -> Hard | 单调收益、变长窗口、最小覆盖模板 | 时序指标滑窗、Token/上下文窗口切分 | ✅ 已就绪 (3题) |
| `04_` | [04_stack_and_queue](./04_stack_and_queue/README.md) | Easy -> Hard | 栈括号匹配、单调递减/递增栈 | JSON/代码括号解析、最大可用矩形与 LLM 参数校验 | ✅ 已就绪 (3题) |
| `05_` | [05_binary_search](./05_binary_search/README.md) | Easy -> Medium | 标准二分边界、旋转数组二分、答案单调二分 | 倒排索引查找、限流阈值与批处理并发寻优 | ✅ 已就绪 (3题) |
| `06_` | [06_linked_list](./06_linked_list/README.md) | Easy -> Hard | 指针重连、快慢指针判环、LRU/LFU 缓存、K 路堆归并 | **LRU/LFU 缓存、循环引用检测、大数据外部归并** | ✅ 已就绪 (5题) |
| `07_` | [07_binary_tree](./07_binary_tree/README.md) | Easy -> Medium | 递归三部曲、BST 校验、最近公共祖先、层序 BFS | 文档解析树（HTML/AST）、索引边界校验与上下文归属 | ✅ 已就绪 (4题) |
| `08_` | [08_backtracking](./08_backtracking/README.md) | Medium -> Hard | 回溯三部曲、树层去重剪枝、排列组合 | 组合配置去重推荐、Agent 动作规划回退 | ✅ 已就绪 (4题) |
| `09_` | [09_greedy](./09_greedy/README.md) | Medium | 排序 + 区间合并、可达最远边界、Kadane 最大子段和 | 调度时间窗、时序峰值区间、RAG 片段融合 | ✅ 已就绪 (3题) |
| `10_` | [10_dynamic_programming](./10_dynamic_programming/README.md) | Easy -> Hard | 动规五部曲、0-1/完全背包、打家劫舍、单词拆分、编辑距离、LIS | **负载均衡、分词匹配、NLP 相似度、重排序列** | ✅ 已就绪 (7题) |
| `11_` | [11_heap_and_trie](./11_heap_and_trie/README.md) | Medium | 最小堆 Top-K、原地三路快选、字典树 Trie | **海量数据 Top-K、搜索补全/分词词典** | ✅ 已就绪 (2题) |
| `12_` | [12_graph](./12_graph/README.md) | Medium | 邻接表、拓扑判环/出序、网格连通块、并查集、Dijkstra | **LangGraph/Airflow 执行序、实体对齐、图谱最短路** | ✅ 已就绪 (5题) |
| `13_` | [13_bit_and_math](./13_bit_and_math/README.md) | Easy | 异或去偶、位运算压缩 | 布隆过滤器、位图去重、状态压缩 | ✅ 已就绪 (2题) |
| `14_` | [14_hard_capstones](./14_hard_capstones/README.md) | Hard | 双指针/单调栈/双堆数据流、单调队列、树状数组 BIT | **实时流式滑窗极值、动态前缀统计、数据流中位数** | ✅ 已就绪 (4题) |
| 合计 | 15 个专题 | Easy -> Hard | — | — | **总题数 61**（已完成 61，待生成 0） |

## 四、一键验证全部题解
在项目根目录运行下面命令，可一次验证 `00_leetcode` 下的全部 Python 脚本：

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 00_leetcode
```
