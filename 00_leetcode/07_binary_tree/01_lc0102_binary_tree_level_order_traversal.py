"""
[题目编号]: LeetCode 102. 二叉树的层序遍历 (Binary Tree Level Order Traversal)
[难度]: Medium (BFS 必背模板题)
[所属专题]: 07_binary_tree
[前置知识]: LeetCode 104、collections.deque

一、题目描述
给你二叉树的根节点 `root`，返回其节点值的**层序遍历**结果（即逐层地、从左到右访问所有节点，每层作为一个子列表）。

示例:
- 输入: [3, 9, 20, None, None, 15, 7] -> 输出: [[3], [9, 20], [15, 7]]
- 边界: [] -> []；[1] -> [[1]]

二、解法与复杂度
- 思路（标准队列 BFS 模板）:
  - 每次进入外层 `while queue:` 循环时，**立刻用 `level_size = len(queue)` 记录本层节点数**；
  - 内层循环恰好弹出 `level_size` 个节点放进 `level_vals`，同时把它们的左右孩子入队（留给下一轮外层循环处理）。
- 时间复杂度: O(n)
- 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 广度优先搜索 (BFS) 是图搜索、社交网络 N 度好友推荐、组织架构树逐级展开、网络爬虫按层抓取的绝对主力算法。
"""

from __future__ import annotations

from collections import deque


class TreeNode:
    """二叉树节点定义。"""

    def __init__(
        self,
        val: int = 0,
        left: TreeNode | None = None,
        right: TreeNode | None = None,
    ) -> None:
        self.val = val
        self.left = left
        self.right = right


def build_tree_level_order(values: list[int | None]) -> TreeNode | None:
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue: deque[TreeNode] = deque([root])
    idx = 1
    while queue and idx < len(values):
        node = queue.popleft()
        if idx < len(values) and values[idx] is not None:
            node.left = TreeNode(values[idx])  # type: ignore[arg-type]
            queue.append(node.left)
        idx += 1
        if idx < len(values) and values[idx] is not None:
            node.right = TreeNode(values[idx])  # type: ignore[arg-type]
            queue.append(node.right)
        idx += 1
    return root


def level_order(root: TreeNode | None) -> list[list[int]]:
    """BFS 层序遍历核心模板。"""
    if root is None:
        return []

    result: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])

    while queue:
        level_size = len(queue)
        level_vals: list[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level_vals.append(node.val)
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        result.append(level_vals)

    return result


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([3, 9, 20, None, None, 15, 7], [[3], [9, 20], [15, 7]]),
        ([1], [[1]]),
        ([], []),
        ([1, 2, 3, 4, None, None, 5], [[1], [2, 3], [4, 5]]),
    ]
    for arr, expected in cases:
        root = build_tree_level_order(arr)
        assert level_order(root) == expected, f'失败: {arr}'
    print('✅ LeetCode 102 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 102. 二叉树的层序遍历 {'*' * 12}", sep='', end='\n\n')
    arr = [3, 9, 20, None, None, 15, 7]
    print(f'输入树: {arr} -> 层序遍历结果: {level_order(build_tree_level_order(arr))}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
