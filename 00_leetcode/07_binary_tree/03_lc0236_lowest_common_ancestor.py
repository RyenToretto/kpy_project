"""
[题目编号]: LeetCode 236. 二叉树的最近公共祖先 (Lowest Common Ancestor / LCA)
[难度]: Medium (递归三部曲「后序自底向上汇总返回值」教科书级经典题)
[所属专题]: 07_binary_tree
[前置知识]: 07_binary_tree/00_lc0104_maximum_depth_of_binary_tree (二叉树节点与递归返回值)

一、题目描述
给定一个二叉树，找到该树中两个指定节点 `p` 和 `q` 的**最近公共祖先**（一个节点也可以是它自己的祖先）。
例如在 `[3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]` 中：
- `p=5, q=1` -> 最近公共祖先为 `3`
- `p=5, q=4` -> 最近公共祖先为 `5`（`5` 自己就是 `4` 的祖先）

二、解法对比与复杂度
1. 解法一（存储每个节点的父节点指针 `parent` + 集合回溯祖先链）:
   - 思路: 先遍历一次树记录 `parent[node] = father`。接着让 `p` 一路顺着 `parent` 往上爬并把路径放进集合 `ancestors`，再让 `q` 往上爬，第一个撞进 `ancestors` 的就是最近公共祖先！
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)（父指针哈希表）
2. 解法二（后序递归自底向上传递 - 递归三部曲典范）:
   - 思路: 递归函数 `lca(node, p, q)` 的返回值含义：**在 `node` 这棵子树里，如果找到了 `p` 或 `q` 就向上汇报它（若两边都找到了则汇报真正的 LCA）；如果一个都没找到就返回 `None`**。
     1. **终止条件**: 如果 `node is None` 或者 `node is p` 或者 `node is q`，直接返回 `node`！
     2. **递归左右子树**: `left = lca(node.left)`, `right = lca(node.right)`（必须后序遍历，等左右子树都汇报完才能做判断！）。
     3. **单层汇总逻辑**:
        - 若 `left is not None and right is not None`：说明 `p` 和 `q` 分别躲在左、右两侧，那当前 `node` 就是它俩首次交汇的最近公共祖先，返回 `node`！
        - 若只有一边非空（例如 `left` 非空、`right` 为空）：把非空的那一边继续原样往上汇报（可能是找到的单侧节点，也可能是下层已经汇合好的 LCA！）。
   - 时间复杂度: O(n)
   - 空间复杂度: O(h)，h 为树高

三、工程与 AI/大数据实战映射
- **Git 找两个分支的共同祖先 (`git merge-base`) / RAG 文档树节点归属定位**: 当 RAG 分层文档树命中某两个子节点切片时，向上找它们的最近公共父章节，把整节上下文补齐再喂给大模型。
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


def build_tree_and_index(values: list[int | None]) -> tuple[TreeNode | None, dict[int, TreeNode]]:
    """辅助函数：建树并返回 `值 -> 节点` 映射，方便直接拿到 p/q 节点对象。"""
    if not values or values[0] is None:
        return None, {}
    root = TreeNode(values[0])
    by_val: dict[int, TreeNode] = {root.val: root}
    queue: deque[TreeNode] = deque([root])
    idx = 1
    while queue and idx < len(values):
        node = queue.popleft()
        if idx < len(values) and values[idx] is not None:
            left_node = TreeNode(values[idx])  # type: ignore[arg-type]
            node.left = left_node
            by_val[left_node.val] = left_node
            queue.append(left_node)
        idx += 1
        if idx < len(values) and values[idx] is not None:
            right_node = TreeNode(values[idx])  # type: ignore[arg-type]
            node.right = right_node
            by_val[right_node.val] = right_node
            queue.append(right_node)
        idx += 1
    return root, by_val


def lca_parent_map(root: TreeNode | None, p: TreeNode, q: TreeNode) -> TreeNode | None:
    """解法一：记录父指针后向上找第一处祖先交点，最直观好理解。"""
    if root is None:
        return None
    parent: dict[TreeNode, TreeNode | None] = {root: None}
    stack: list[TreeNode] = [root]
    while p not in parent or q not in parent:
        node = stack.pop()
        if node.left is not None:
            parent[node.left] = node
            stack.append(node.left)
        if node.right is not None:
            parent[node.right] = node
            stack.append(node.right)

    ancestors: set[TreeNode] = set()
    curr: TreeNode | None = p
    while curr is not None:
        ancestors.add(curr)
        curr = parent[curr]

    curr = q
    while curr is not None:
        if curr in ancestors:
            return curr
        curr = parent[curr]
    return None


def lca_recursive(root: TreeNode | None, p: TreeNode, q: TreeNode) -> TreeNode | None:
    """解法二：后序递归自底向上汇总，O(h) 空间、无需额外父指针表。"""
    if root is None or root is p or root is q:
        return root

    left = lca_recursive(root.left, p, q)
    right = lca_recursive(root.right, p, q)

    if left is not None and right is not None:
        return root  # 左右各找到一个，当前节点正是首次交汇的最近公共祖先
    return left if left is not None else right


def run_tests() -> None:
    """自动化断言测试，覆盖异侧分支、上下祖先关系与最小两节点树。"""
    tree_vals = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]
    root, nodes = build_tree_and_index(tree_vals)
    assert root is not None

    cases = [
        (5, 1, 3),   # 分居左右子树
        (5, 4, 5),   # p 本身就是 q 的祖先
        (7, 4, 2),   # 深层兄弟节点
        (6, 4, 5),   # 左孙与右孙交汇于 5
    ]
    for solver in (lca_parent_map, lca_recursive):
        for pv, qv, expected_val in cases:
            ans = solver(root, nodes[pv], nodes[qv])
            assert ans is nodes[expected_val], f'{solver.__name__} 失败: p={pv}, q={qv}'

    # 两节点极简边界树
    small_root, small_nodes = build_tree_and_index([1, 2])
    for solver in (lca_parent_map, lca_recursive):
        assert solver(small_root, small_nodes[1], small_nodes[2]) is small_nodes[1]

    print('✅ LeetCode 236 (最近公共祖先) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 236. 二叉树的最近公共祖先 {'*' * 12}", sep='', end='\n\n')
    root, nodes = build_tree_and_index([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
    ans = lca_recursive(root, nodes[5], nodes[4])
    print('节点 5 与 4 的最近公共祖先值:', None if ans is None else ans.val)
    run_tests()


if __name__ == '__main__':
    bootstrap()
