"""
[题目编号]: LeetCode 125. 验证回文串 (Valid Palindrome)
[难度]: Easy
[所属专题]: 02_two_pointers
[前置知识]: 字符串方法 isalnum() / lower()、左右双指针

一、题目描述
如果在将所有大写字符转换为小写字符、并移除所有非字母数字字符之后，短语正着读和反着读都一样，则认为它是一个回文串。

示例:
- 输入: s = "A man, a plan, a canal: Panama" -> True ("amanaplanacanalpanama")
- 输入: s = "race a car" -> False
- 边界: " " -> True；"0P" -> False (注意数字 '0' 也是合法字符，不能只用 isalpha！)

二、解法对比与复杂度
1. 解法一（先清洗过滤，再切片反转）:
   - 思路: 用列表推导式过滤出 `ch.lower()`（仅保留 `ch.isalnum()`），再看 `cleaned == cleaned[::-1]`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)
2. 解法二（左右相向双指针原地比对 - O(1) 空间）:
   - 思路: `left` 从左往右、`right` 从右往左，遇到标点空格直接跳过，遇到字母数字就转小写比对，一旦不等立刻返回 `False`。
   - 时间复杂度: O(n)
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 文本预处理 (Text Normalization): 做 RAG 文档清洗与密码/用户输入校验时，需要决定是「生成新字符串」还是「原地扫描省内存」。
"""

from __future__ import annotations


def is_palindrome_clean(s: str) -> bool:
    """解法一：先过滤清洗成纯小写字母数字串，再反转比较。"""
    cleaned = [ch.lower() for ch in s if ch.isalnum()]
    return cleaned == cleaned[::-1]


def is_palindrome_two_pointers(s: str) -> bool:
    """解法二：左右双指针，原地跳过非字母数字字符，空间复杂度 O(1)。"""
    left, right = 0, len(s) - 1

    while left < right:
        # 左指针跳过标点、空格等非字母数字字符
        while left < right and not s[left].isalnum():
            left += 1
        # 右指针跳过非字母数字字符
        while left < right and not s[right].isalnum():
            right -= 1

        if s[left].lower() != s[right].lower():
            return False

        left += 1
        right -= 1

    return True


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ('A man, a plan, a canal: Panama', True),
        ('race a car', False),
        (' ', True),
        ('0P', False),
        ('a.', True),
    ]
    for solver in (is_palindrome_clean, is_palindrome_two_pointers):
        for s, expected in cases:
            assert solver(s) is expected, f'{solver.__name__} 失败: s={s!r}'
    print('✅ LeetCode 125 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 125. 验证回文串 {'*' * 12}", sep='', end='\n\n')
    sample = 'A man, a plan, a canal: Panama'
    print(f'测试文本: {sample!r} -> {is_palindrome_two_pointers(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
