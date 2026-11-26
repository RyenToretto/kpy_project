"""
[题目编号]: LeetCode 226. 翻转二叉树 (Invert Binary Tree)
[难度]: Easy (树递归交换左右子树)
[所属专题]: 07_binary_tree
[前置知识]: 07_binary_tree/00_lc0104、递归三部曲

一、题目描述
给你一棵二叉树的根节点 `root`，翻转这棵二叉树，并返回其根节点（每个节点的左右孩子互换）。

示例:
- [4, 2, 7, 1, 3, 6, 9] -> [4, 7, 2, 9, 6, 3, 1]
- [] -> []

二、解法
1. 递归 DFS: 交换当前左右指针，再递归翻转左右子树。O(n)/O(h)
2. BFS 层序: 队列遍历每个节点时交换左右孩子。O(n)/O(n)

三、工程映射
- 镜像布局 / AST 改写: UI 树镜像、表达式树左右交换做代数变形。
"""

from __future__ import annotations

from collections import deque


class TreeNode:
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


def tree_to_level_list(root: TreeNode | None) -> list[int | None]:
    if root is None:
        return []
    out: list[int | None] = []
    queue: deque[TreeNode | None] = deque([root])
    while queue:
        node = queue.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def invert_tree_dfs(root: TreeNode | None) -> TreeNode | None:
    if root is None:
        return None
    root.left, root.right = root.right, root.left
    invert_tree_dfs(root.left)
    invert_tree_dfs(root.right)
    return root


def invert_tree_bfs(root: TreeNode | None) -> TreeNode | None:
    if root is None:
        return None
    queue: deque[TreeNode] = deque([root])
    while queue:
        node = queue.popleft()
        node.left, node.right = node.right, node.left
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return root


def run_tests() -> None:
    cases = [
        ([4, 2, 7, 1, 3, 6, 9], [4, 7, 2, 9, 6, 3, 1]),
        ([2, 1, 3], [2, 3, 1]),
        ([], []),
        ([1], [1]),
    ]
    for values, expected in cases:
        for solver in (invert_tree_dfs, invert_tree_bfs):
            root = build_tree_level_order(values)
            actual = tree_to_level_list(solver(root))
            assert actual == expected, f'{solver.__name__} 失败: {values}'
    print('✅ LeetCode 226 (翻转二叉树) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 226. 翻转二叉树 {'*' * 12}", sep='', end='\n\n')
    print(tree_to_level_list(invert_tree_dfs(build_tree_level_order([4, 2, 7, 1, 3, 6, 9]))))
    run_tests()


if __name__ == '__main__':
    bootstrap()
