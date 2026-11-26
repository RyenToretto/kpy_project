"""
[题目编号]: LeetCode 200. 岛屿数量 (Number of Islands)
[难度]: Medium
[所属专题]: 12_graph
[前置知识]: 二维列表遍历、递归 DFS、collections.deque 队列、四个方向的邻居

一、题目描述
给你一个由 '1'（陆地）和 '0'（水）组成的二维网格，计算岛屿的数量。
岛屿由水平或垂直方向相邻的陆地连接而成，网格四周都被水包围。
- 输入: [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]] -> 输出 1
- 输入: [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]] -> 输出 3
- 边界: 空网格 [] -> 输出 0

二、解法对比
1. 解法一（直观版：递归 DFS 淹没岛屿）:
   - 思路: 遍历每个格子，遇到陆地就计数一次，然后用递归把与它相连的整片陆地都改成 '0'（“淹没”），避免重复计数。
   - 时间复杂度: O(M × N)，每个格子最多访问一次
   - 空间复杂度: O(M × N)（最坏情况下递归栈深度可达格子总数，大网格可能栈溢出）
2. 解法二（最优版：迭代 BFS 队列 + 访问标记）:
   - 思路: 同样遍历每个格子，遇到未访问的陆地就计数，然后用队列做广度优先搜索，把相连的陆地全部标记为已访问。
     队列是显式的，不依赖递归栈，所以大网格也安全。
   - 时间复杂度: O(M × N)
   - 空间复杂度: O(min(M, N))～O(M × N)（队列的最大长度取决于岛屿形状）

三、工程与 AI/大数据实战映射
- **连通分量统计**: 社交网络里的社群数量、设备组网的子网数量，都是“数连通块”的问题。
- **图像处理**: 图片中的连通区域（如细胞计数、卫星图像中的水域）就是这道题的二维版本。
- **知识图谱 / RAG**: 检索结果中彼此关联的文档簇，可以用同样的 BFS 把它们归为一组。
"""

from __future__ import annotations

from collections import deque

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # 上、下、左、右四个方向


def solve_bruteforce(grid: list[list[str]]) -> int:
    """解法一：递归 DFS，遇到陆地就把整片岛屿改成水，避免重复计数。内部先复制一份网格，不修改调用方的输入。"""
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    grid = [row[:] for row in grid]  # 先复制一份，尽量不破坏调用方的数据

    def sink(r: int, c: int) -> None:
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return  # 越界或者已经是水，直接返回
        grid[r][c] = '0'  # 淹没当前陆地
        for dr, dc in DIRECTIONS:
            sink(r + dr, c + dc)  # 递归淹没相邻陆地

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':  # 发现一座新岛屿
                count += 1
                sink(r, c)
    return count


def solve_optimal(grid: list[list[str]]) -> int:
    """解法二：迭代 BFS，用显式队列代替递归栈，并用 visited 集合标记访问过的格子。"""
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    visited: set[tuple[int, int]] = set()
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != '1' or (r, c) in visited:
                continue  # 水或已经访问过的陆地，跳过
            count += 1  # 发现新岛屿
            visited.add((r, c))
            queue: deque[tuple[int, int]] = deque([(r, c)])
            while queue:  # 广度优先搜索整座岛屿
                cur_r, cur_c = queue.popleft()
                for dr, dc in DIRECTIONS:
                    nr, nc = cur_r + dr, cur_c + dc
                    in_bounds = 0 <= nr < rows and 0 <= nc < cols
                    if in_bounds and grid[nr][nc] == '1' and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
    return count


def run_tests() -> None:
    """自动化断言测试：覆盖单岛、多岛、空网格、全是水与对角线不相连的情况。"""
    grid_one = [
        ['1', '1', '1', '1', '0'],
        ['1', '1', '0', '1', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '0', '0', '0'],
    ]
    grid_three = [
        ['1', '1', '0', '0', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '1', '0', '0'],
        ['0', '0', '0', '1', '1'],
    ]
    grid_diagonal = [  # 对角线相连不算相邻，应该是 2 座岛
        ['1', '0'],
        ['0', '1'],
    ]
    cases = [
        (grid_one, 1),
        (grid_three, 3),
        (grid_diagonal, 2),
        ([], 0),  # 边界：空网格
        ([['0', '0'], ['0', '0']], 0),  # 全是水
    ]
    for grid, expected in cases:
        assert solve_bruteforce(grid) == expected
        assert solve_optimal(grid) == expected

    # 调用方的网格不应该被修改（解法一内部复制了一份）
    assert grid_one[0][0] == '1'
    print('✅ 岛屿数量所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 200. 岛屿数量 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例
    sample = [
        ['1', '1', '0', '0', '0'],
        ['1', '1', '0', '0', '0'],
        ['0', '0', '1', '0', '0'],
        ['0', '0', '0', '1', '1'],
    ]
    print(f'示例网格的岛屿数量 = {solve_optimal(sample)}')
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
