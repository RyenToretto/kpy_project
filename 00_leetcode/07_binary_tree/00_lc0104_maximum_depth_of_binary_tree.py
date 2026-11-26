"""
[题目编号]: LeetCode 104. 二叉树的最大深度 (Maximum Depth of Binary Tree)
[难度]: Easy (树与递归入门第一题)
[所属专题]: 07_binary_tree
[前置知识]: class TreeNode、递归思想、collections.deque 层序遍历

一、题目描述
给定一个二叉树 `root`，返回其最大深度（从根节点到最远叶子节点的最长路径上的节点数）。
本文件自带 `build_tree_level_order` 工具函数，支持用类似 `[3, 9, 20, None, None, 15, 7]` 的层序列表直接建树！

示例:
- 输入: [3, 9, 20, None, None, 15, 7] -> 输出: 3
- 边界: [] -> 0；[1] -> 1

二、解法对比与复杂度
1. 解法一（递归 DFS：分治思想）:
   - 思路: 一棵树的最大深度 = `1 + max(左子树深度, 右子树深度)`；空节点深度为 `0`。
   - 时间复杂度: O(n)，每个节点访问一次。
   - 空间复杂度: O(h)，h 为树高（递归调用栈深度，最坏退化成链表时 O(n)）。
2. 解法二（迭代 BFS：队列按层计数）:
   - 思路: 用 `deque` 一层一层往下扫，每扫完一整层 `depth += 1`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 文档解析与语法分析: 解析 HTML/Markdown 层级标题深度、计算决策树最大深度防止过拟合、限制递归推理树 (Tree of Thoughts) 最大步数，原理相通。
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
    """辅助函数：根据 LeetCode 标准层序数组构建二叉树。"""
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


def max_depth_dfs(root: TreeNode | None) -> int:
    """解法一：递归 DFS，代码极简，体会“把大问题拆成左右子树子问题”。"""
    if root is None:
        return 0
    left_depth = max_depth_dfs(root.left)
    right_depth = max_depth_dfs(root.right)
    return 1 + max(left_depth, right_depth)


def max_depth_bfs(root: TreeNode | None) -> int:
    """解法二：迭代 BFS，一层一层遍历并记录总层数。"""
    if root is None:
        return 0

    queue: deque[TreeNode] = deque([root])
    depth = 0

    while queue:
        level_size = len(queue)  # 关键：先锁死当前层有多少个节点
        for _ in range(level_size):
            node = queue.popleft()
            if node.left is not None:
                queue.append(node.left)
            if node.right is not None:
                queue.append(node.right)
        depth += 1

    return depth


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([3, 9, 20, None, None, 15, 7], 3),
        ([1, None, 2], 2),
        ([1], 1),
        ([], 0),
    ]
    for solver in (max_depth_dfs, max_depth_bfs):
        for arr, expected in cases:
            root = build_tree_level_order(arr)
            assert solver(root) == expected, f'{solver.__name__} 失败: {arr}'
    print('✅ LeetCode 104 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 104. 二叉树的最大深度 {'*' * 12}", sep='', end='\n\n')
    arr = [3, 9, 20, None, None, 15, 7]
    root = build_tree_level_order(arr)
    print(f'树数组: {arr}, 最大深度 = {max_depth_dfs(root)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
