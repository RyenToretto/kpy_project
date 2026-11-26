"""
[题目编号]: LeetCode 21. 合并两个有序链表 (Merge Two Sorted Lists)
[难度]: Easy (多路归并的基础积木，服务 LC 23)
[所属专题]: 06_linked_list
[前置知识]: 哨兵节点、双指针

一、题目描述
将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接两个给定链表的所有节点组成的。

示例:
- [1, 2, 4] + [1, 3, 4] -> [1, 1, 2, 3, 4, 4]
- [] + [] -> []
- [] + [0] -> [0]

二、解法
迭代哨兵版: 每次把较小头节点接到结果尾部；某一边耗尽后，把另一边剩余整段接上。
时间 O(m+n)，空间 O(1)（只改指针）。

三、工程映射
- 两路有序流归并: 日志按时间戳合并、倒排列表求交并前的有序合并；也是 LC 23 K 路归并的最小单元。
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


def merge_two_lists(list1: ListNode | None, list2: ListNode | None) -> ListNode | None:
    """迭代哨兵合并两条有序链表。"""
    dummy = ListNode(0)
    tail = dummy
    while list1 is not None and list2 is not None:
        if list1.val <= list2.val:
            tail.next = list1
            list1 = list1.next
        else:
            tail.next = list2
            list2 = list2.next
        tail = tail.next
    tail.next = list1 if list1 is not None else list2
    return dummy.next


def run_tests() -> None:
    cases = [
        ([1, 2, 4], [1, 3, 4], [1, 1, 2, 3, 4, 4]),
        ([], [], []),
        ([], [0], [0]),
        ([5], [1, 2, 4], [1, 2, 4, 5]),
    ]
    for a, b, expected in cases:
        actual = linked_list_to_list(merge_two_lists(build_linked_list(a), build_linked_list(b)))
        assert actual == expected, f'失败: {a}+{b} -> {actual}'
    print('✅ LeetCode 21 (合并两个有序链表) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 21. 合并两个有序链表 {'*' * 12}", sep='', end='\n\n')
    print(linked_list_to_list(merge_two_lists(build_linked_list([1, 2, 4]), build_linked_list([1, 3, 4]))))
    run_tests()


if __name__ == '__main__':
    bootstrap()
