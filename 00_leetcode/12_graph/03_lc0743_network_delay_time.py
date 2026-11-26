"""
[题目编号]: LeetCode 743. 网络延迟时间 (Network Delay Time / Dijkstra 最短路)
[难度]: Medium (加权有向图 Dijkstra 第一标准模板题，参考 kamyu104 heap Dijkstra 重写为 Python 3.12 教学版)
[所属专题]: 12_graph
[前置知识]: 12_graph/00_lc0207_course_schedule (邻接表建图)、heapq 小顶堆

一、题目描述
有 `n` 个网络节点，标记为 `1` 到 `n`。
给你一个列表 `times`，表示信号经过有向边的传递时间：`times[i] = [u, v, w]`，其中 `u` 是源节点，`v` 是目标节点，`w` 是一个信号从 `u` 传递到 `v` 所需的非负时间。
现在，从某个节点 `k` 发出一个信号。需要多久才能使**所有节点**都收到信号？如果不能使所有节点收到信号，返回 `-1`。

示例:
- 输入: times = [[2, 1, 1], [2, 3, 1], [3, 4, 1]], n = 4, k = 2 -> 输出: 2
- 输入: times = [[1, 2, 1]], n = 2, k = 1 -> 输出: 1
- 输入: times = [[1, 2, 1]], n = 2, k = 2 -> 输出: -1 (节点 1 无法收到)

二、解法对比与复杂度（注意：边权非负才能用 Dijkstra！）
1. 解法一（Bellman-Ford 松弛 n-1 轮）:
   - 思路: 对全部 `E` 条边重复松弛 `n - 1` 轮。代码极短且能处理负权边，但在稀疏图上较慢。
   - 时间复杂度: O(V * E)
   - 空间复杂度: O(V)
2. 解法二（堆优化 Dijkstra - 贪心 + 小顶堆，工程标准写法）:
   - 思路:
     1. `dist[x]` 记录从起点 `k` 到 `x` 目前已知的最短耗时，初始为 `inf`，`dist[k] = 0`。
     2. 用小顶堆存 `(当前累计耗时 d, 节点 u)`，每次弹出全局耗时最小的节点。
     3. **核心去重剪枝**：如果 `d > dist[u]`，说明堆里存的是以前入队的过期旧路径，直接 `continue` 跳过（无需实现堆内 decrease-key！）。
     4. 用 `u` 去松弛它的邻居 `v`：若 `d + w < dist[v]`，更新 `dist[v]` 并入堆。
     5. 所有节点都算出最短到达时间后，取 `max(dist[1:])`；若仍有 `inf` 说明存在不可达节点，返回 `-1`。
   - 时间复杂度: O((V + E) log V)
   - 空间复杂度: O(V + E)

三、工程与 AI/大数据实战映射
- **微服务路由与多跳知识图谱检索 (GraphRAG)**: 找成本/延迟最低的服务链路、在带权重的关系图谱中从查询实体出发计算最高相关度（最小代价）的多跳子图，核心都是堆优化 Dijkstra。
"""

from __future__ import annotations

import heapq


def network_delay_bellman_ford(times: list[list[int]], n: int, k: int) -> int:
    """解法一：Bellman-Ford，重复松弛所有边 n-1 次，时间 O(V * E)。"""
    inf = float('inf')
    dist = [inf] * (n + 1)
    dist[k] = 0

    for _ in range(n - 1):
        updated = False
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    ans = max(dist[1:])
    return -1 if ans == inf else int(ans)


def network_delay_dijkstra(times: list[list[int]], n: int, k: int) -> int:
    """解法二：堆优化 Dijkstra 最短路，时间 O((V + E) log V)。"""
    adj: list[list[tuple[int, int]]] = [[] for _ in range(n + 1)]
    for u, v, w in times:
        adj[u].append((v, w))

    inf = float('inf')
    dist = [inf] * (n + 1)
    dist[k] = 0
    min_heap: list[tuple[int, int]] = [(0, k)]

    while min_heap:
        curr_dist, u = heapq.heappop(min_heap)
        # 懒惰删除：如果弹出的是过期路径（已有更短路径），直接跳过
        if curr_dist > dist[u]:
            continue
        for nxt, weight in adj[u]:
            cand = curr_dist + weight
            if cand < dist[nxt]:
                dist[nxt] = cand
                heapq.heappush(min_heap, (cand, nxt))

    ans = max(dist[1:])
    return -1 if ans == inf else int(ans)


def run_tests() -> None:
    """自动化断言测试，含重边覆盖、零权边与不可达节点用例。"""
    cases = [
        ([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2, 2),
        ([[1, 2, 1]], 2, 1, 1),
        ([[1, 2, 1]], 2, 2, -1),
        ([[1, 2, 10], [1, 3, 2], [3, 2, 3], [2, 4, 1]], 4, 1, 6),  # 1->3->2->4 更短
        ([[1, 2, 5], [1, 2, 1]], 2, 1, 1),  # 平行重边取更小的
        ([], 1, 1, 0),  # 只有 1 个节点，起点即终点
    ]
    for solver in (network_delay_bellman_ford, network_delay_dijkstra):
        for times, n, k, expected in cases:
            actual = solver(times, n, k)
            assert actual == expected, f'{solver.__name__} 失败: n={n}, k={k} -> {actual}'
    print('✅ LeetCode 743 (Dijkstra) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 743. 网络延迟时间 (Dijkstra) {'*' * 12}", sep='', end='\n\n')
    times = [[1, 2, 10], [1, 3, 2], [3, 2, 3], [2, 4, 1]]
    print(f'4 节点带权图从 1 出发全网耗时: {network_delay_dijkstra(times, 4, 1)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
