"""
[题目编号]: LeetCode 20. 有效的括号 (Valid Parentheses)
[难度]: Easy
[所属专题]: 04_stack_and_queue
[前置知识]: list 作为栈 (append 入栈、pop 出栈)、dict 映射

一、题目描述
给定一个只包括 `'('`, `')'`, `'{'`, `'}'`, `'['`, `']'` 的字符串 `s`，判断字符串是否有效：
1. 左括号必须用相同类型的右括号闭合；
2. 左括号必须以正确的顺序闭合；
3. 每个右括号都有一个对应的相同类型的左括号。

示例:
- 输入: s = "()[]{}" -> True
- 输入: s = "([)]" -> False
- 输入: s = "{[]}" -> True
- 边界: "" -> True；"(" -> False；"]" -> False

二、解法与复杂度
- 思路（栈 + 映射字典）:
  - 遇到左括号就入栈等待匹配；
  - 遇到右括号时，检查栈是否为空（空了说明右括号多出来），再弹出栈顶看是否恰好是配对的左括号；
  - 全部扫描结束后，只有栈为空（`not stack`）才说明全部成对消完。
- 时间复杂度: O(n)
- 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- JSON / 代码块修复与校验: 大模型输出 JSON 或 SQL 时偶尔会少闭括号，流式解析器修复截断 JSON 的底层逻辑就是基于本题的栈追踪未闭合括号！
"""

from __future__ import annotations


def is_valid_parentheses(s: str) -> bool:
    """用 Python list 当作栈 + 右括号映射表实现 O(n) 括号匹配。"""
    # 奇数长度绝对不可能完全两两配对，提前快速剪枝
    if len(s) % 2 == 1:
        return False

    pairs = {
        ')': '(',
        ']': '[',
        '}': '{',
    }
    stack: list[str] = []

    for ch in s:
        if ch in pairs:
            # 遇到右括号：如果栈为空，或者栈顶不是对应的左括号，立刻失败
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()
        else:
            # 遇到左括号：压入栈中等待后续右括号来抵消
            stack.append(ch)

    return not stack


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('()', True),
        ('()[]{}', True),
        ('(]', False),
        ('([)]', False),
        ('{[]}', True),
        ('', True),
        ('(', False),
        ('))', False),
    ]
    for s, expected in cases:
        assert is_valid_parentheses(s) is expected, f'失败: s={s!r}'
    print('✅ LeetCode 20 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 20. 有效的括号 {'*' * 12}", sep='', end='\n\n')
    for text in ('{[]}', '([)]'):
        print(f'{text!r} 是否有效: {is_valid_parentheses(text)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
