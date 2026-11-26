"""
[题目编号]: LeetCode 412. Fizz Buzz
[难度]: Easy
[所属专题]: 00_warmup_basics
[前置知识]: chapter03_sign (`%` 取余)、chapter04_if_elif_else、chapter05_match (`match/case`)

一、题目描述
给你一个整数 `n`，返回一个长度为 `n` 的字符串列表 `answer`（下标从 1 开始计数）：
- 如果 `i` 同时是 3 和 5 的倍数，输出 `"FizzBuzz"`
- 如果 `i` 是 3 的倍数，输出 `"Fizz"`
- 如果 `i` 是 5 的倍数，输出 `"Buzz"`
- 否则输出字符串 `str(i)`

示例:
- 输入: n = 5
- 输出: ["1", "2", "Fizz", "4", "Buzz"]
- 边界: n = 0 -> []；n = 1 -> ["1"]；n = 15 -> 最后一个为 "FizzBuzz"

二、解法对比与复杂度
1. 解法一（经典 if/elif/else 分支，注意优先级！）:
   - 思路: 必须先判断 `i % 15 == 0`（或同时被 3 和 5 整除），否则会被 `i % 3 == 0` 提前拦截。这和你 `00_interview/leap_year` 先判断 400 的优先级思路完全一致！
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)（返回值所需空间）
2. 解法二（Python 3.10+ match/case 模式匹配版）:
   - 思路: 构造元组 `(i % 3 == 0, i % 5 == 0)` 做模式匹配，语义非常直观。
   - 时间复杂度: O(n)
   - 空间复杂度: O(n)

三、工程与 AI/大数据实战映射
- 规则引擎 / 数据打标: 在做数据集清洗、风控规则路由时，「多个规则条件重叠时谁优先命中」是极高频的工程 bug 来源。
"""

from __future__ import annotations


def fizz_buzz_if(n: int) -> list[str]:
    """解法一：经典 if/elif/else，必须把最严格的条件 (同时被 3 和 5 整除) 放最前面。"""
    answer: list[str] = []
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            answer.append('FizzBuzz')
        elif i % 3 == 0:
            answer.append('Fizz')
        elif i % 5 == 0:
            answer.append('Buzz')
        else:
            answer.append(str(i))
    return answer


def fizz_buzz_match(n: int) -> list[str]:
    """解法二：延续 chapter05_match 与 exp_leap_year_03.py 的元组模式匹配风格。"""
    answer: list[str] = []
    for i in range(1, n + 1):
        match (i % 3 == 0, i % 5 == 0):
            case (True, True):
                answer.append('FizzBuzz')
            case (True, False):
                answer.append('Fizz')
            case (False, True):
                answer.append('Buzz')
            case _:
                answer.append(str(i))
    return answer


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        (0, []),
        (1, ['1']),
        (3, ['1', '2', 'Fizz']),
        (5, ['1', '2', 'Fizz', '4', 'Buzz']),
        (
            15,
            [
                '1', '2', 'Fizz', '4', 'Buzz',
                'Fizz', '7', '8', 'Fizz', 'Buzz',
                '11', 'Fizz', '13', '14', 'FizzBuzz',
            ],
        ),
    ]
    for solver in (fizz_buzz_if, fizz_buzz_match):
        for n, expected in cases:
            actual = solver(n)
            assert actual == expected, f'{solver.__name__} 失败: n={n}, 实际={actual}'
    print('✅ LeetCode 412 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 412. Fizz Buzz {'*' * 12}", sep='', end='\n\n')
    print(f'n=15 输出: {fizz_buzz_match(15)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
