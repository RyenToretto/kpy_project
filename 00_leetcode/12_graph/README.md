# `12_graph` | 图论与拓扑排序专题

- **学习阶段**: 第 4 阶段
- **前置语法**: 邻接表 `defaultdict(list)`、`collections.deque`、入度表 `indegree`
- **为什么学它**: 无论大数据计算框架（Airflow / Spark DAG），还是 AI Agent 多步骤工作流编排（LangGraph / 工作流依赖检测），底层都是**有向无环图 (DAG) 与拓扑排序**！

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 207. 课程表 | Medium | Kahn 队列拓扑排序检测有向环 | [00_lc0207_course_schedule.py](./00_lc0207_course_schedule.py) | ✅ 已完成 |
| `01_` | LeetCode 200. 岛屿数量 | Medium | 网格 DFS/BFS 连通块计数 | [`01_lc0200_number_of_islands.py`](./01_lc0200_number_of_islands.py) | ✅ 已完成 |
| `02_` | LeetCode 684. 冗余连接 | Medium | 并查集 Union-Find（路径压缩 + 按规模合并） | [02_lc0684_redundant_connection.py](./02_lc0684_redundant_connection.py) | ✅ 已完成 |
| `03_` | LeetCode 743. 网络延迟时间 | Medium | 堆优化 Dijkstra 带权最短路 vs Bellman-Ford | [03_lc0743_network_delay_time.py](./03_lc0743_network_delay_time.py) | ✅ 已完成 |
