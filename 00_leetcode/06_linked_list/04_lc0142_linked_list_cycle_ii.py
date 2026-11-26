"""
[题目编号]: LeetCode 142. 环形链表 II (Linked List Cycle II / 顺带覆盖 LC 141 判环)
[难度]: Medium (双指针判环与入环点定位经典题)
[所属专题]: 06_linked_list
[前置知识]: 06_linked_list/00_lc0206_reverse_linked_list (链表节点)、快慢双指针

一、题目描述
给定一个链表的头节点 `head`，返回链表**开始入环的第一个节点**。如果链表无环，则返回 `None`。
（进阶要求：用 `O(1)` 额外空间解决，不能修改链表。）

示例:
- 输入: 节点 [3, 2, 0, -4]，尾节点连回下标 1（值为 2）-> 返回值为 2 的那个节点
- 输入: 节点 [1, 2]，尾节点连回下标 0 -> 返回值为 1 的那个节点
- 边界: [] -> None；单节点无环 [1] -> None；单节点自环 -> 返回自己

二、解法对比与复杂度
1. 解法一（`set` 记录已访问节点对象 - 最直观无脑稳）:
   - 思路: 沿着链表走，把访问过的节点对象 `node` 放进集合 `seen`；第一个重复遇到的节点就是入环点！
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)
2. 解法二（Floyd 龟兔赛跑快慢双指针 - O(1) 空间最优）:
   - 第一步（判环，即 LC 141）：`slow` 每次走 1 步、`fast` 每次走 2 步。若 `fast` 走到 `None` 则无环；若 `slow == fast` 相遇，则一定有环。
   - 第二步（找入环口）：设起点到入环口距离为 `a`，入环口到相遇点距离为 `b`，环剩余部分为 `c`（环长 `L = b + c`）。
     相遇时慢指针走了 `a + b`，快指针走了 `a + b + k*(b + c)`，又因为快指针步数是慢指针 2 倍：
     `2(a + b) = a + b + k(b + c)` => **`a = (k - 1)(b + c) + c`**！
     意思是：**让一个指针从链表头 `head` 出发、另一个指针从相遇点 `slow` 出发，两人同步每次走 1 步，最终必定恰好在入环口撞上**！
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- **图谱/配置/Agent 死循环与循环引用检测**: 在对象引用链、软链接解析、有向链表任务流（如用户配置了 A->B->C->B 的回环跳转）中定位真正造成环的起点，避免只报错却找不到谁连错了。
"""

from __future__ import annotations


class ListNode:
    """单链表节点定义。"""

    def __init__(self, val: int = 0, next_node: ListNode | None = None) -> None:
        self.val = val
        self.next = next_node


def build_cycle_list(values: list[int], pos: int) -> tuple[ListNode | None, ListNode | None]:
    """辅助函数：根据列表与环入口下标 pos (-1 表示无环) 构建测试链表，返回 (head, 期望入环节点)。"""
    if not values:
        return None, None
    nodes = [ListNode(v) for v in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]
    entry = None
    if 0 <= pos < len(nodes):
        nodes[-1].next = nodes[pos]
        entry = nodes[pos]
    return nodes[0], entry


def detect_cycle_hash(head: ListNode | None) -> ListNode | None:
    """解法一：哈希集合存已走过的节点对象引用，第一个撞到的就是环入口，O(n) 空间。"""
    seen: set[ListNode] = set()
    curr = head
    while curr is not None:
        if curr in seen:
            return curr
        seen.add(curr)
        curr = curr.next
    return None


def detect_cycle_two_pointers(head: ListNode | None) -> ListNode | None:
    """解法二：Floyd 快慢双指针，判环 + 同速相遇找入环口，O(1) 额外空间。"""
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        assert slow is not None
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            # 相遇后，ptr1 从起点、ptr2 从相遇点同步每次走 1 步，必在入环口相遇
            ptr1 = head
            ptr2 = slow
            while ptr1 is not ptr2:
                assert ptr1 is not None and ptr2 is not None
                ptr1 = ptr1.next
                ptr2 = ptr2.next
            return ptr1

    return None


def run_tests() -> None:
    """自动化断言测试：用对象身份 `is` 验证返回的正是原始环入口节点。"""
    cases = [
        ([3, 2, 0, -4], 1),
        ([1, 2], 0),
        ([1], 0),
        ([1], -1),
        ([1, 2, 3, 4], -1),
        ([1, 2, 3, 4, 5], 3),
        ([], -1),
    ]
    for solver in (detect_cycle_hash, detect_cycle_two_pointers):
        for values, pos in cases:
            head, expected_entry = build_cycle_list(values, pos)
            actual = solver(head)
            assert actual is expected_entry, f'{solver.__name__} 失败: values={values}, pos={pos}'
    print('✅ LeetCode 142 (环形链表 II) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 142. 环形链表 II {'*' * 12}", sep='', end='\n\n')
    head, _ = build_cycle_list([3, 2, 0, -4], pos=1)
    entry = detect_cycle_two_pointers(head)
    print('链表 [3, 2, 0, -4] (尾连回下标 1) 检测到入环节点值:', None if entry is None else entry.val)
    run_tests()


if __name__ == '__main__':
    bootstrap()
