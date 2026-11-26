"""
[题目编号]: LeetCode 210. 课程表 II (Course Schedule II)
[难度]: Medium (拓扑排序从「判环」进阶到「输出顺序」)
[所属专题]: 12_graph
[前置知识]: 12_graph/00_lc0207_course_schedule (Kahn 判环)

一、题目描述
现在你总共有 `num_courses` 门课需要选，记为 `0` 到 `num_courses - 1`。
给你一个数组 `prerequisites`，其中 `prerequisites[i] = [a_i, b_i]`，表示如果要学习课程 `a_i`，则必须先学习课程 `b_i`。
返回你为了学完所有课程所安排的学习顺序。可能会有多个正确的顺序，你只要返回任意一种。如果不可能完成所有课程，返回空数组。

示例:
- 输入: num_courses = 2, prerequisites = [[1, 0]] -> [0, 1]
- 输入: num_courses = 4, prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]] -> [0, 1, 2, 3] 或 [0, 2, 1, 3]
- 边界: 有环 [[0, 1], [1, 0]] -> []；无依赖 num_courses=3, [] -> [0, 1, 2]（任意全排列均可）

二、解法对比与复杂度
与 LC 207 几乎相同：仍然是 Kahn 算法（入度 + BFS）。唯一差别是把「计数是否等于 n」改成「把弹出顺序收集成答案」；若最终答案长度 < n，说明有环，返回空列表。

- 时间复杂度: O(V + E)
- 空间复杂度: O(V + E)

三、工程与 AI/大数据实战映射
- Airflow / LangGraph / Agent 工作流编排: 207 只告诉你「有没有死锁」，210 才给出真正可执行的拓扑顺序。
"""

from __future__ import annotations

from collections import deque


def find_order(num_courses: int, prerequisites: list[list[int]]) -> list[int]:
    """Kahn 拓扑排序：返回任意一种合法修课顺序；有环则返回空列表。"""
    graph: list[list[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses
    for course, pre in prerequisites:
        graph[pre].append(course)
        indegree[course] += 1

    queue: deque[int] = deque(i for i in range(num_courses) if indegree[i] == 0)
    order: list[int] = []

    while queue:
        curr = queue.popleft()
        order.append(curr)
        for nxt in graph[curr]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)

    return order if len(order) == num_courses else []


def is_valid_order(num_courses: int, prerequisites: list[list[int]], order: list[int]) -> bool:
    """校验：顺序长度正确，且每条先修边都满足「先学 pre 再学 course」。"""
    if len(order) != num_courses:
        return False
    position = {course: idx for idx, course in enumerate(order)}
    if len(position) != num_courses:
        return False
    return all(position[pre] < position[course] for course, pre in prerequisites)


def run_tests() -> None:
    """自动化断言测试。"""
    # 1. 简单两门课
    order = find_order(2, [[1, 0]])
    assert order == [0, 1]

    # 2. 多解：只要合法即可
    prereqs = [[1, 0], [2, 0], [3, 1], [3, 2]]
    order = find_order(4, prereqs)
    assert is_valid_order(4, prereqs, order)

    # 3. 有环必须返回空
    assert find_order(2, [[1, 0], [0, 1]]) == []
    assert find_order(3, [[0, 1], [1, 2], [2, 0]]) == []

    # 4. 无依赖：返回包含全部课程的任意排列
    order = find_order(3, [])
    assert sorted(order) == [0, 1, 2]

    # 5. 单门课
    assert find_order(1, []) == [0]

    print('✅ LeetCode 210 (课程表 II / 拓扑顺序) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 210. 课程表 II {'*' * 12}", sep='', end='\n\n')
    prereqs = [[1, 0], [2, 0], [3, 1], [3, 2]]
    print(f'先修关系 {prereqs} -> 修课顺序: {find_order(4, prereqs)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
