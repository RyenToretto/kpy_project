"""
[题目编号]: LeetCode 206. 反转链表 (Reverse Linked List)
[难度]: Easy (链表入门必刷第一题)
[所属专题]: 06_linked_list
[前置知识]: class 节点定义、对象引用 (next 指针)、while 循环

一、题目描述
给你单链表的头节点 `head`，请你反转链表，并返回反转后的链表头节点。
本文件自带 `build_linked_list` 和 `linked_list_to_list` 工具函数，方便你在本地直接用普通列表构造并查看链表！

示例:
- 输入: [1, 2, 3, 4, 5] -> 输出: [5, 4, 3, 2, 1]
- 边界: [] -> []；[1] -> [1]

二、解法对比与复杂度
1. 解法一（迭代三指针 - 最实用面试版）:
   - 思路: 用 `prev = None` 和 `curr = head` 向前推进。每次改变 `curr.next = prev` 前，**务必先用 `nxt = curr.next` 把后续节点存好**，防止链表断掉！
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)
2. 解法二（递归版 - 锻炼递归思维）:
   - 思路: 假设 `reverse_list_recursive(head.next)` 已经帮我们反转好了后面的链条，只需让 `head.next.next = head`，再断开 `head.next = None`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)（递归调用栈空间）

三、工程与 AI/大数据实战映射
- 链式结构与不可变日志: Git 提交历史回溯、对话历史多轮消息链表拼接与逆序渲染，背后都是指针链条操作。
"""

from __future__ import annotations


class ListNode:
    """单链表节点定义。"""

    def __init__(self, val: int = 0, next_node: ListNode | None = None) -> None:
        self.val = val
        self.next = next_node


def build_linked_list(values: list[int]) -> ListNode | None:
    """辅助函数：把 Python 列表转换成单链表，方便本地测试。"""
    dummy = ListNode(0)
    tail = dummy
    for val in values:
        tail.next = ListNode(val)
        tail = tail.next
    return dummy.next


def linked_list_to_list(head: ListNode | None) -> list[int]:
    """辅助函数：把单链表还原成 Python 列表，方便断言和打印。"""
    result: list[int] = []
    curr = head
    while curr is not None:
        result.append(curr.val)
        curr = curr.next
    return result


def reverse_list_iterative(head: ListNode | None) -> ListNode | None:
    """解法一：迭代反转链表，空间复杂度 O(1)，工程最推荐。"""
    prev: ListNode | None = None
    curr = head

    while curr is not None:
        nxt = curr.next  # 1. 先暂存下一个节点，否则修改指针后就找不到后面了
        curr.next = prev  # 2. 调转箭头指向前一个节点
        prev = curr  # 3. prev 往前挪一步
        curr = nxt  # 4. curr 往前挪一步

    return prev  # 循环结束时 curr 为 None，prev 正好是新表头


def reverse_list_recursive(head: ListNode | None) -> ListNode | None:
    """解法二：递归反转，适合训练对子问题与函数调用栈的理解。"""
    if head is None or head.next is None:
        return head

    new_head = reverse_list_recursive(head.next)
    head.next.next = head  # 让原来的下一个节点反过来指向自己
    head.next = None  # 断开原本的正向指针，防止形成环！
    return new_head


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
        ([1, 2], [2, 1]),
        ([1], [1]),
        ([], []),
    ]
    for solver in (reverse_list_iterative, reverse_list_recursive):
        for raw, expected in cases:
            head = build_linked_list(raw)
            actual = linked_list_to_list(solver(head))
            assert actual == expected, f'{solver.__name__} 失败: 输入={raw}, 实际={actual}'
    print('✅ LeetCode 206 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 206. 反转链表 {'*' * 12}", sep='', end='\n\n')
    raw = [1, 2, 3, 4, 5]
    reversed_head = reverse_list_iterative(build_linked_list(raw))
    print(f'原链表: {raw} -> 反转后: {linked_list_to_list(reversed_head)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
