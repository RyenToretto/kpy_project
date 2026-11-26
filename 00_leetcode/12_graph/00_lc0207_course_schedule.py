"""
[题目编号]: LeetCode 207. 课程表 (Course Schedule)
[难度]: Medium (图论与拓扑排序必刷第一题)
[所属专题]: 12_graph
[前置知识]: collections.deque、邻接表、图与入度概念

一、题目描述
你这个学期必须选修 `num_courses` 门课程，记为 `0` 到 `num_courses - 1`。
在选修某些课程之前需要一些先修课程。先修课程按数组 `prerequisites` 给出，其中 `[a, b]` 表示：如果要学习课程 `a`，则**必须先学习课程 `b`**（即存在一条有向边 `b -> a`）。
请你判断是否可能完成所有课程的学习（等价于：判断有向图中**是否存在环**）。

示例:
- 输入: num_courses = 2, prerequisites = [[1, 0]] -> True (先学 0，再学 1)
- 输入: num_courses = 2, prerequisites = [[1, 0], [0, 1]] -> False (互相依赖形成死锁环！)
- 边界: num_courses = 1, prerequisites = [] -> True

二、解法与复杂度
- 思路（Kahn 算法：入度表 + 队列 BFS 拓扑排序）:
  1. `indegree[x]` 记录课程 `x` 还剩多少门前置课没学；`graph[pre]` 存学完 `pre` 后能解锁哪些后续课程。
  2. 先把所有 `indegree == 0`（没有前置依赖、可直接开学的课程）全部放进队列。
  3. 每次从队列取出一门已完成的课 `curr`（已完成计数 `finished += 1`），把它的后续课程入度减 1；如果有后续课入度归 0，说明前置条件全解锁了，加入队列！
  4. 最后看 `finished == num_courses`：如果相等说明全部解锁，无环；如果不等，说明剩下的节点互相卡在环里。
- 时间复杂度: O(V + E)，V 为课程数，E 为先修关系数。
- 空间复杂度: O(V + E)

三、工程与 AI/大数据实战映射
- **AI Agent / Airflow / Spark 工作流引擎 (DAG)**: 多个 Agent 节点或数据 ETL 任务存在上下游依赖时，调度器启动前必须跑一遍拓扑排序：一是为了找出正确执行顺序，二是为了防止用户配置出死循环依赖（Cycle Detection）！
"""

from __future__ import annotations

from collections import deque


def can_finish(num_courses: int, prerequisites: list[list[int]]) -> bool:
    """Kahn 算法：基于入度和 BFS 队列进行拓扑排序。"""
    graph: list[list[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses

    # 建图：[course, pre] 表示必须先学 pre 再学 course，即 pre -> course
    for course, pre in prerequisites:
        graph[pre].append(course)
        indegree[course] += 1

    # 所有不需要前置课程的节点率先入队
    queue: deque[int] = deque(i for i in range(num_courses) if indegree[i] == 0)
    finished = 0

    while queue:
        curr = queue.popleft()
        finished += 1
        for nxt in graph[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    return finished == num_courses


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        (2, [[1, 0]], True),
        (2, [[1, 0], [0, 1]], False),
        (4, [[1, 0], [2, 0], [3, 1], [3, 2]], True),
        (3, [[0, 1], [1, 2], [2, 0]], False),
        (1, [], True),
    ]
    for num_courses, prereqs, expected in cases:
        assert can_finish(num_courses, prereqs) is expected, f'失败: {num_courses}, {prereqs}'
    print('✅ LeetCode 207 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 207. 课程表 (拓扑排序) {'*' * 12}", sep='', end='\n\n')
    print(f'DAG 无环课程表是否可完成: {can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]])}')
    print(f'互相依赖死锁是否可完成: {can_finish(2, [[1, 0], [0, 1]])}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
