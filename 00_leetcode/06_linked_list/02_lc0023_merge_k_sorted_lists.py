"""
[题目编号]: LeetCode 23. 合并 K 个升序链表 (Merge k Sorted Lists)
[难度]: Hard (多路归并核心模板题，参考 kamyu104 思路重写为 Python 3.12 教学版)
[所属专题]: 06_linked_list
[前置知识]: 06_linked_list/00_lc0206_reverse_linked_list (链表与哨兵节点)、heapq 小顶堆、分治合并

一、题目描述
给你一个链表数组 `lists`，每个链表都已经按升序排列。请你将所有链表合并到一个升序链表中，返回合并后的链表。

示例:
- 输入: lists = [[1, 4, 5], [1, 3, 4], [2, 6]] -> 输出: [1, 1, 2, 3, 4, 4, 5, 6]
- 边界: [] -> []；[[], []] -> []；只有一条链表 [[1, 2]] -> [1, 2]

二、解法对比与复杂度（设总共 `N` 个节点，共 `k` 条链表）
1. 解法一（顺序逐条合并）:
   - 思路: 先合并第 1 条和第 2 条，再用结果去合并第 3 条……前两条的节点会被重复扫描最多 k 次。
   - 时间复杂度: O(k * N)
   - 空间复杂度: O(1)
2. 解法二（小顶堆多路归并 - 实时流式大数据核心套路）:
   - 思路: 维护一个容量最多为 `k` 的小顶堆，存放每条链表「当前最靠前的那个节点」。
     每次弹出全局最小的节点接进结果，并把该节点所在链表的下一个节点补进堆里。
     **Python 工程小坑**：`ListNode` 本身不能比较大小！当两个节点的 `val` 相等时，元组 `(node.val, node)` 会尝试直接比较 `node < node` 而报 `TypeError`！因此在堆里放入 `(node.val, idx, node)`，用递增序号 `idx` 打破平局。
   - 时间复杂度: O(N log k)
   - 空间复杂度: O(k)（堆大小只与路数 k 有关，就算每路 10 亿条数据也不爆内存！）
3. 解法三（分治两两归并 - 不依赖堆、同样最优）:
   - 思路: 像归并排序一样两两配对合并，每轮链表数量减半，共 `log k` 轮。
   - 时间复杂度: O(N log k)
   - 空间复杂度: O(1)（迭代版两两合并）或 O(log k)（递归栈）

三、工程与 AI/大数据实战映射
- **大数据外部排序 (External Merge Sort)**: 内存装不下的 TB 级日志先分片排好序落盘成 k 个有序文件，再用「k 路小顶堆归并」流式合成全局有序大文件。
- **RAG 多路召回融合 / 倒排索引交并集**: 多个分片或多种检索路同时返回按分数排序的有序文档流时，可用多路归并高效汇总。
"""

from __future__ import annotations

import heapq


class ListNode:
    """单链表节点定义。"""

    def __init__(self, val: int = 0, next_node: ListNode | None = None) -> None:
        self.val = val
        self.next = next_node


def build_linked_list(values: list[int]) -> ListNode | None:
    """辅助函数：把普通列表转成单链表。"""
    dummy = ListNode(0)
    tail = dummy
    for val in values:
        tail.next = ListNode(val)
        tail = tail.next
    return dummy.next


def linked_list_to_list(head: ListNode | None) -> list[int]:
    """辅助函数：把单链表转回普通列表，方便打印和断言。"""
    out: list[int] = []
    curr = head
    while curr is not None:
        out.append(curr.val)
        curr = curr.next
    return out


def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    """合并两条有序链表（基础积木）。"""
    dummy = ListNode(0)
    tail = dummy
    while l1 is not None and l2 is not None:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 is not None else l2
    return dummy.next


def merge_k_lists_heap(lists: list[ListNode | None]) -> ListNode | None:
    """解法一：小顶堆 k 路归并，时间 O(N log k)、堆空间 O(k)。"""
    min_heap: list[tuple[int, int, ListNode]] = []
    for idx, node in enumerate(lists):
        if node is not None:
            # 传入 idx 作为次级比较键，避免节点值相等时比较 ListNode 触发 TypeError
            heapq.heappush(min_heap, (node.val, idx, node))

    dummy = ListNode(0)
    tail = dummy
    tie_breaker = len(lists)

    while min_heap:
        _, _, smallest = heapq.heappop(min_heap)
        tail.next = smallest
        tail = tail.next
        if smallest.next is not None:
            tie_breaker += 1
            heapq.heappush(min_heap, (smallest.next.val, tie_breaker, smallest.next))

    tail.next = None
    return dummy.next


def merge_k_lists_divide_conquer(lists: list[ListNode | None]) -> ListNode | None:
    """解法二：迭代两两配对分治合并，时间 O(N log k)、额外空间 O(1)。"""
    if not lists:
        return None
    curr = list(lists)
    while len(curr) > 1:
        merged_round: list[ListNode | None] = []
        for i in range(0, len(curr), 2):
            left_list = curr[i]
            right_list = curr[i + 1] if i + 1 < len(curr) else None
            merged_round.append(merge_two_lists(left_list, right_list))
        curr = merged_round
    return curr[0]


def run_tests() -> None:
    """自动化断言测试，特别验证「节点值相等」不会触发 heapq 比较报错。"""
    cases = [
        ([[1, 4, 5], [1, 3, 4], [2, 6]], [1, 1, 2, 3, 4, 4, 5, 6]),
        ([[1, 1, 1], [1, 1], [1]], [1, 1, 1, 1, 1, 1]),
        ([[-5, 0, 3], [], [-2, 4]], [-5, -2, 0, 3, 4]),
        ([[], []], []),
        ([], []),
        ([[42]], [42]),
    ]
    for solver in (merge_k_lists_heap, merge_k_lists_divide_conquer):
        for raw_lists, expected in cases:
            linked_inputs = [build_linked_list(item) for item in raw_lists]
            actual = linked_list_to_list(solver(linked_inputs))
            assert actual == expected, f'{solver.__name__} 失败: {raw_lists} -> {actual}'
    print('✅ LeetCode 23 (合并 K 个升序链表) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 23. 合并 K 个升序链表 {'*' * 12}", sep='', end='\n\n')
    raw = [[1, 4, 5], [1, 3, 4], [2, 6]]
    merged = merge_k_lists_heap([build_linked_list(x) for x in raw])
    print(f'多路输入: {raw} -> 归并结果: {linked_list_to_list(merged)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
