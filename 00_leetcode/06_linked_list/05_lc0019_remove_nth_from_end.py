"""
[题目编号]: LeetCode 19. 删除链表的倒数第 N 个结点 (Remove Nth Node From End of List)
[难度]: Medium (双指针间距模板)
[所属专题]: 06_linked_list
[前置知识]: 06_linked_list/00_lc0206_reverse_linked_list、哨兵节点

一、题目描述
给你一个链表，删除链表的倒数第 `n` 个结点，并且返回链表的头结点。

示例:
- [1, 2, 3, 4, 5], n=2 -> [1, 2, 3, 5]
- [1], n=1 -> []
- [1, 2], n=1 -> [1]

二、解法
1. 先数长度再删: 两遍扫描，O(n)
2. 双指针间距: 哨兵 `dummy`；`fast` 先走 n+1 步，再 `slow/fast` 同步前进，直到 `fast` 到末尾。
   此时 `slow` 正好停在「待删节点的前驱」。一次扫描 O(n)，空间 O(1)。

三、工程映射
- 流式窗口滞后删除: 只保留最近 n 条边的滑动缓冲里删除相对末尾第 n 条记录。
"""

from __future__ import annotations


class ListNode:
    def __init__(self, val: int = 0, next_node: ListNode | None = None) -> None:
        self.val = val
        self.next = next_node


def build_linked_list(values: list[int]) -> ListNode | None:
    dummy = ListNode(0)
    tail = dummy
    for val in values:
        tail.next = ListNode(val)
        tail = tail.next
    return dummy.next


def linked_list_to_list(head: ListNode | None) -> list[int]:
    out: list[int] = []
    curr = head
    while curr is not None:
        out.append(curr.val)
        curr = curr.next
    return out


def remove_nth_from_end_length(head: ListNode | None, n: int) -> ListNode | None:
    """解法一：先数长度再定位删除。"""
    length = 0
    curr = head
    while curr is not None:
        length += 1
        curr = curr.next
    dummy = ListNode(0, head)
    prev = dummy
    for _ in range(length - n):
        assert prev.next is not None
        prev = prev.next
    assert prev.next is not None
    prev.next = prev.next.next
    return dummy.next


def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    """解法二：快慢指针间距 n+1，一次扫描。"""
    dummy = ListNode(0, head)
    fast: ListNode | None = dummy
    slow: ListNode | None = dummy
    for _ in range(n + 1):
        assert fast is not None
        fast = fast.next
    while fast is not None:
        assert slow is not None
        fast = fast.next
        slow = slow.next
    assert slow is not None and slow.next is not None
    slow.next = slow.next.next
    return dummy.next


def run_tests() -> None:
    cases = [
        ([1, 2, 3, 4, 5], 2, [1, 2, 3, 5]),
        ([1], 1, []),
        ([1, 2], 1, [1]),
        ([1, 2], 2, [2]),
    ]
    for solver in (remove_nth_from_end_length, remove_nth_from_end):
        for raw, n, expected in cases:
            actual = linked_list_to_list(solver(build_linked_list(raw), n))
            assert actual == expected, f'{solver.__name__} 失败: {raw}, n={n}'
    print('✅ LeetCode 19 (删除倒数第 N 个结点) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 19. 删除链表的倒数第 N 个结点 {'*' * 12}", sep='', end='\n\n')
    print(linked_list_to_list(remove_nth_from_end(build_linked_list([1, 2, 3, 4, 5]), 2)))
    run_tests()


if __name__ == '__main__':
    bootstrap()
