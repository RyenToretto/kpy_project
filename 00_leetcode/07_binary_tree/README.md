# `07_binary_tree` | 二叉树与 DFS / BFS 专题

- **学习阶段**: 第 3 阶段
- **前置语法**: 递归函数、`collections.deque`（队列）、`class TreeNode`
- **为什么学它**: 树结构是计算机科学最核心的模型之一：文件系统目录、HTML DOM 树、Python 语法树 (AST)、RAG 文档层级分块树 (RAPTOR / 标题树)、决策树模型全都是树。

## 递归三部曲（参考《代码随想录》思维框架）
写二叉树递归不再靠猜，每次按这三步定型：
1. **确定递归函数的参数和返回值**：需要从下层收结果（如深度/LCA），还是靠全局变量/上下界往下传？
2. **确定终止条件**：遇到 `root is None`（空节点）或命中目标时返回什么？
3. **确定单层递归逻辑**：前序（先处理当前节点再递归左右）、中序（BST 递增校验）还是后序（等左右子树都汇报完毕再汇总）？

## 顺序刷题清单（从 `00_` 开始）

| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | LeetCode 104. 二叉树的最大深度 | Easy | 递归 DFS 后序 vs 队列 BFS 层序 | [00_lc0104_maximum_depth_of_binary_tree.py](./00_lc0104_maximum_depth_of_binary_tree.py) | ✅ 已完成 |
| `01_` | LeetCode 102. 二叉树的层序遍历 | Medium | `deque` 按层快照 `len(queue)` 模板 | [01_lc0102_binary_tree_level_order_traversal.py](./01_lc0102_binary_tree_level_order_traversal.py) | ✅ 已完成 |
| `02_` | LeetCode 98. 验证二叉搜索树 | Medium | 上下界 `(low, high)` 区间递归 vs 中序严格递增校验 | [02_lc0098_validate_binary_search_tree.py](./02_lc0098_validate_binary_search_tree.py) | ✅ 已完成 |
| `03_` | LeetCode 236. 二叉树的最近公共祖先 | Medium | 后序递归自底向上汇总返回值 vs 父指针表回溯 | [03_lc0236_lowest_common_ancestor.py](./03_lc0236_lowest_common_ancestor.py) | ✅ 已完成 |
