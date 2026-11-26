"""
[主题]: 异常处理 (try / except / else / finally、自定义异常、重试)
[来源]: jackfrued/Python-100-Days 第 20~21 天「异常处理」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 00_basic 语法主线、函数、分支、01_python_100_days/00_file_io (文件读写)

一、主题说明
程序一定会遇到坏数据、缺文件、网络超时。异常处理的目标是：
- 只捕获自己能处理的错误，不要用裸 except 把所有问题吞掉；
- 把底层错误翻译成业务上能看懂的错误（自定义异常）；
- 对偶发错误做有限次重试，但要有上限，避免无限循环。

二、解法对比（以「把字符串转成正整数」为例）
1. 直观版 parse_positive_basic: 裸 except，任何错误都返回 -1，调用方无法区分原因（反面教材）。
   - 时间复杂度 O(字符串长度)，空间复杂度 O(1)
2. 进阶版 parse_positive: 只捕获 ValueError，并抛出自定义的 InvalidAgeError，错误原因清楚。
   - 时间复杂度 O(字符串长度)，空间复杂度 O(1)
3. 重试版 call_with_retry: 最多尝试 max_attempts 次，每次只针对可重试的异常；次数用完后把最后一次异常抛出。
   - 时间复杂度 O(max_attempts)，空间复杂度 O(1)

三、真实用途
- 大数据: 清洗数据时坏行不能让整个作业失败，要记录后跳过（逐行 try/except）。
- AI Agent / RAG: 调用大模型 API 经常遇到限流与超时，有上限的重试是标准做法。
- 数据分析: 用户输入、Excel 脏数据的校验，都依赖清晰的异常类型。
- 全栈开发: 接口参数校验失败要返回明确的 4xx 错误，而不是 500 崩溃。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar('T')  # 泛型占位符：retry 的返回值类型与被调用函数一致


class InvalidAgeError(ValueError):
    """自定义异常：继承 ValueError，表示「年龄输入不合法」这一业务错误。"""


class TemporaryServiceError(Exception):
    """自定义异常：表示临时性故障（如网络抖动、限流），值得重试。"""


def parse_positive_basic(text: str) -> int:
    """直观版：裸 except 吞掉所有错误，只能返回 -1，调用方无法知道原因。"""
    try:
        value = int(text)
        return value if value > 0 else -1
    except:  # noqa: E722 反面教材：裸 except 会连 KeyboardInterrupt 一起吞掉
        return -1


def parse_positive(text: str) -> int:
    """进阶版：只捕获 ValueError，并转换为业务异常，保留原始错误链。"""
    try:
        value = int(text)  # 非数字会抛出 ValueError
    except ValueError as exc:
        raise InvalidAgeError(f'年龄必须是整数，收到: {text!r}') from exc  # from 保留原始异常
    else:
        # else 块只在 try 成功时执行，把业务规则判断放在这里更清楚
        if value <= 0:
            raise InvalidAgeError(f'年龄必须大于 0，收到: {value}')
        return value
    finally:
        # finally 无论成功失败都会执行，常用于释放资源；这里只演示用法
        pass


def call_with_retry(
    action: Callable[[], T],
    max_attempts: int = 3,
    retry_on: tuple[type[Exception], ...] = (TemporaryServiceError,),
) -> T:
    """有上限的重试：只重试 retry_on 中的异常，超过次数后抛出最后一次的异常。"""
    if max_attempts < 1:
        raise ValueError('max_attempts 至少为 1')
    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            return action()  # 成功就直接返回
        except retry_on as exc:  # 只拦截“可重试”的异常，其它异常直接向外抛
            last_error = exc
    assert last_error is not None  # 循环至少执行一次，这里一定有错误
    raise last_error


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例、异常用例与边界用例。"""
    # 1. 合法输入
    assert parse_positive('18') == 18
    assert parse_positive_basic('18') == 18

    # 2. 非法输入：进阶版抛出业务异常，并且能看到原始 ValueError
    try:
        parse_positive('abc')
    except InvalidAgeError as exc:
        assert isinstance(exc.__cause__, ValueError)  # from 保留了原始异常
    else:
        raise AssertionError('非数字必须抛出 InvalidAgeError')

    # 3. 非正数：业务规则拦截
    try:
        parse_positive('0')
    except InvalidAgeError:
        pass
    else:
        raise AssertionError('0 不是合法年龄')

    # 直观版返回 -1，无法区分“非数字”与“非正数”
    assert parse_positive_basic('abc') == -1
    assert parse_positive_basic('0') == -1

    # 4. 重试：前两次失败、第三次成功 -> 返回成功结果
    attempts = {'count': 0}

    def flaky() -> str:
        attempts['count'] += 1
        if attempts['count'] < 3:
            raise TemporaryServiceError('模拟限流')
        return 'ok'

    assert call_with_retry(flaky, max_attempts=3) == 'ok'
    assert attempts['count'] == 3

    # 5. 重试次数耗尽：抛出最后一次的临时错误
    def always_fail() -> str:
        raise TemporaryServiceError('一直失败')

    try:
        call_with_retry(always_fail, max_attempts=2)
    except TemporaryServiceError:
        pass
    else:
        raise AssertionError('重试耗尽后必须抛出异常')

    # 6. 不可重试的异常直接抛出，不会浪费次数
    def wrong_input() -> str:
        raise InvalidAgeError('参数错误')

    try:
        call_with_retry(wrong_input, max_attempts=5)
    except InvalidAgeError:
        pass
    else:
        raise AssertionError('非临时性异常必须直接抛出')

    print('✅ 异常处理所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 异常处理 {'*' * 12}", sep='', end='\n\n')
    for raw in ['18', 'abc', '-3']:
        try:
            print(f'输入 {raw!r} -> 年龄 {parse_positive(raw)}')
        except InvalidAgeError as exc:
            print(f'输入 {raw!r} -> 业务错误: {exc}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
