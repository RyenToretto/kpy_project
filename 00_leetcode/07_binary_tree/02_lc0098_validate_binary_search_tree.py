"""
[题目编号]: LeetCode 98. 验证二叉搜索树 (Validate Binary Search Tree / BST)
[难度]: Medium (二叉树递归三部曲必刷防坑题)
[所属专题]: 07_binary_tree
[前置知识]: 07_binary_tree/00_lc0104_maximum_depth_of_binary_tree (TreeNode 与建树)、中序遍历

一、题目描述
给你一个二叉树的根节点 `root`，判断其是否是一个有效的二叉搜索树 (BST)：
- 节点的左子树**只包含严格小于**当前节点的数；
- 节点的右子树**只包含严格大于**当前节点的数；
- 所有左子树和右子树自身也必须是二叉搜索树。

**新手第一大坑**：不能只检查 `node.left.val < node.val < node.right.val`！
例如 `[5, 4, 6, None, None, 3, 7]`：虽然 `6` 的左孩子 `3 < 6`，但 `3` 在 `5` 的右子树里却比 `5` 小，这是**非法** BST！

二、解法对比与复杂度
1. 解法一（上下界区间传递递归法 - 最优且直指 BST 定义）:
   - 思路: 向下递归时把允许的范围 `(low, high)` 一并传下去！
     往左子树走，上界收紧成 `node.val` -> `(low, node.val)`；
     往右子树走，下界收紧成 `node.val` -> `(node.val, high)`。
     只要节点不满足 `low < node.val < high`，立刻返回 `False`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(h)，h 为树高
2. 解法二（中序遍历严格递增校验 - BST 黄金性质）:
   - 思路: 二叉搜索树的中序遍历（左 -> 根 -> 右）结果**一定是严格单调递增序列**！
     用变量 `prev_val` 记录上一个中序访问到的值（或先中序收集列表），只要当前值 `<= prev_val` 就返回 `False`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(h)（迭代栈版 / 递归栈版）

三、工程与 AI/大数据实战映射
- **数据库 B+ 树索引页与范围分区校验**: 有序索引树要求整棵子树键值严格落在上级分割区间 `[low, high)` 内，范围边界传入法正是索引一致性检查 (consistency check) 的基础。
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
    """辅助函数：根据层序列表构建二叉树。"""
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


def is_valid_bst_bounds(root: TreeNode | None) -> bool:
    """解法一：传递上下界 (low, high) 递归验证整棵子树区间合法性。"""
    def check(node: TreeNode | None, low: float, high: float) -> bool:
        if node is None:
            return True
        if not (low < node.val < high):
            return False
        # 左子树不能超过当前节点值；右子树不能低于当前节点值
        return check(node.left, low, node.val) and check(node.right, node.val, high)

    return check(root, float('-inf'), float('inf'))


def is_valid_bst_inorder(root: TreeNode | None) -> bool:
    """解法二：迭代中序遍历，校验访问序列是否严格递增。"""
    stack: list[TreeNode] = []
    curr = root
    prev_val = float('-inf')

    while curr is not None or stack:
        while curr is not None:
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()
        # BST 中序遍历必须严格递增，相等（重复值）也不合法
        if curr.val <= prev_val:
            return False
        prev_val = curr.val
        curr = curr.right

    return True


def run_tests() -> None:
    """自动化断言测试，特别覆盖“局部合法但全局跨界”的经典反例。"""
    cases = [
        ([2, 1, 3], True),
        ([5, 1, 4, None, None, 3, 6], False),
        ([5, 4, 6, None, None, 3, 7], False),  # 经典坑：3<6 但 3 在 5 的右子树里！
        ([2, 2, 2], False),                    # 严格小于/大于：重复值不算合法 BST
        ([0], True),
        ([], True),
        ([-2147483648, None, 2147483647], True),
    ]
    for solver in (is_valid_bst_bounds, is_valid_bst_inorder):
        for arr, expected in cases:
            root = build_tree_level_order(arr)
            actual = solver(root)
            assert actual is expected, f'{solver.__name__} 失败: {arr} -> {actual}'
    print('✅ LeetCode 98 (验证二叉搜索树) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 98. 验证二叉搜索树 {'*' * 12}", sep='', end='\n\n')
    trap_tree = [5, 4, 6, None, None, 3, 7]
    print(f'经典陷阱树 {trap_tree} 是否合法 BST: {is_valid_bst_bounds(build_tree_level_order(trap_tree))}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
