"""
[题目编号]: LeetCode 684. 冗余连接 (Redundant Connection / 并查集模板)
[难度]: Medium (并查集 Union-Find 标准第一模板题，参考 kamyu104 思路重写为 Python 3.12 教学版)
[所属专题]: 12_graph
[前置知识]: 图与树（n 个节点连通无环的树恰好有 n-1 条边）、递归与路径压缩

一、题目描述
树可以看成是一个**连通且无环**的无向图。
给定往一棵 `n` 个节点（节点值 `1..n`）的树中添加一条额外边后的图：输入数组 `edges` 共有 `n` 条边 `[u, v]`。
请找出一条可以删去的边，使得剩下的图重新成为一棵树。如果有多个答案，返回在 `edges` 中**最后出现**的那条边。

示例:
- 输入: edges = [[1, 2], [1, 3], [2, 3]] -> 输出: [2, 3]
- 输入: edges = [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]] -> 输出: [1, 4]

二、解法对比与复杂度
1. 解法一（每次加边前用 DFS 检查两点是否已连通）:
   - 思路: 逐条加入边 `(u, v)`；加之前先跑一次 DFS 看 `u` 和 `v` 是否已经能互相到达，如果已经可达，那新边必定成环！
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(n)
2. 解法二（并查集 Union-Find：路径压缩 + 按秩合并）:
   - 思路: 为每个节点维护所属集合的「代表元 `parent[x]`」。
     - `find(x)`: 沿父指针往上找根节点，同时把沿途节点**直接挂到根下（路径压缩）**，下次查询接近 O(1)！
     - `union(x, y)`: 找到两边的根 `rx, ry`。若 `rx == ry`，说明 `x` 和 `y` **早就属于同一连通块**，当前这条边就是制造环的多余边！否则把小树挂到大树下面（按规模/秩合并）。
   - 时间复杂度: O(n * alpha(n)) ≈ O(n)（alpha 为反阿克曼函数，可视为常数）
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- **大数据实体对齐 / 知识图谱去重合并 (Entity Resolution)**: 在客户主数据合并、RAG 知识图谱等价实体消歧中，大量「A=B」「B=C」等价关系需要秒级合并成连通簇并检测冲突。
- **社交网络 / 反欺诈团伙发现**: 账户-设备-IP 关联图里，用并查集快速聚出共享同一黑产设备的连通子图。
"""

from __future__ import annotations

from collections import defaultdict


class UnionFind:
    """标准并查集模板（带路径压缩 + 按集合大小合并），刷题与工程可直接复用。"""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.comp_size = [1] * size  # 记录每棵树的节点数，小树挂到大树上保持扁平

    def find(self, x: int) -> int:
        """查找根节点，并在回溯时执行路径压缩。"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """合并 x 与 y：若原本就在同一集合返回 False（成环），否则合并后返回 True。"""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.comp_size[rx] < self.comp_size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.comp_size[rx] += self.comp_size[ry]
        return True


def find_redundant_connection_dfs(edges: list[list[int]]) -> list[int]:
    """解法一：逐边加图并用 DFS 判定两点是否已可达，O(n^2)。"""
    graph: dict[int, list[int]] = defaultdict(list)

    def reachable(src: int, dst: int, seen: set[int]) -> bool:
        if src == dst:
            return True
        seen.add(src)
        return any(nxt not in seen and reachable(nxt, dst, seen) for nxt in graph[src])

    for u, v in edges:
        if u in graph and v in graph and reachable(u, v, set()):
            return [u, v]
        graph[u].append(v)
        graph[v].append(u)
    return []


def find_redundant_connection_uf(edges: list[list[int]]) -> list[int]:
    """解法二：并查集一次遍历检测成环边，均摊时间 O(n)。"""
    # 节点编号是 1..n，共有 len(edges) 个节点，开辟 len(edges)+1 长度即可免去减 1 偏移
    uf = UnionFind(len(edges) + 1)
    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]
    return []


def run_tests() -> None:
    """自动化断言测试，含并查集独立连通块断言与图成环边界测试。"""
    # 1. 验证并查集基础连通性
    uf = UnionFind(5)
    assert uf.union(1, 2) is True
    assert uf.union(2, 3) is True
    assert uf.find(1) == uf.find(3)
    assert uf.union(1, 3) is False  # 已连通，再连必成环

    # 2. 对照测试两种解法
    cases = [
        ([[1, 2], [1, 3], [2, 3]], [2, 3]),
        ([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]], [1, 4]),
        ([[3, 4], [1, 2], [2, 4], [3, 5], [2, 5]], [2, 5]),
        ([[1, 2], [2, 1]], [2, 1]),
    ]
    for solver in (find_redundant_connection_dfs, find_redundant_connection_uf):
        for edges, expected in cases:
            assert solver(edges) == expected, f'{solver.__name__} 失败: {edges}'
    print('✅ LeetCode 684 (并查集) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 684. 冗余连接 (并查集) {'*' * 12}", sep='', end='\n\n')
    edges = [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]
    print(f'边列表: {edges} -> 应删除的成环冗余边: {find_redundant_connection_uf(edges)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
