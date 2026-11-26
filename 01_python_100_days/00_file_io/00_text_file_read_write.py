"""
[主题]: 文件读写与路径处理 (open / with / pathlib)
[来源]: jackfrued/Python-100-Days 第 21 天「文件读写」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 字符串与函数 (语法主线 00_basic/chapter01~05 之后)、for 循环、异常基础

一、主题说明
文件读写是数据工程的第一步：读日志、读 CSV、写清洗结果都要用到。
- 用 with 语句打开文件，离开代码块自动关闭，避免句柄泄漏、数据卡在缓冲区没写入。
- 用 pathlib.Path 拼接路径，Windows / macOS / Linux 通用，不用手写 '/' 或 '\\'。
- 写文本时统一指定 encoding='utf-8'，否则中文在不同系统上可能乱码。

二、解法对比（同一件事的三种写法）
1. 直观版 write_read_basic: open + close 手动关闭，容易忘记 close。
   - 时间复杂度 O(文件大小)，空间复杂度 O(文件大小)（read 一次性读入）
2. 进阶版 write_read_with: with 语句自动关闭，逐行迭代不一次性占满内存。
   - 时间复杂度 O(文件大小)，空间复杂度 O(总行数)（这里为了演示返回列表）
3. 进阶版 append_and_count_lines: 追加模式 'a' 不覆盖旧内容，逐行统计行数。
   - 时间复杂度 O(文件大小)，空间复杂度 O(1)（流式遍历，不保存内容）

三、真实用途
- 大数据: 逐行流式读取 GB 级日志，避免 read() 一次性撑爆内存。
- 数据分析: 先用文本读取拿到原始数据，再交给 Pandas 清洗。
- AI Agent / RAG: 读取本地文档切块入库，第一步就是可靠的文件读取。
- 全栈开发: 写配置、导出报表、保存上传文件都依赖这套 API。
"""

from __future__ import annotations

import tempfile
from pathlib import Path


def write_read_basic(file_path: Path, lines: list[str]) -> str:
    """直观版：手动 open / close，逻辑清楚，但必须记得关闭文件。"""
    f = open(file_path, mode='w', encoding='utf-8')  # 写模式打开；mode='w' 会清空原有内容
    for line in lines:  # 逐行写入
        f.write(line + '\n')  # 手动补上换行符
    f.close()  # 必须手动关闭，否则数据可能还留在缓冲区里

    f = open(file_path, mode='r', encoding='utf-8')  # 读模式重新打开
    content = f.read()  # 一次性把整个文件读成一个字符串
    f.close()
    return content


def write_read_with(file_path: Path, lines: list[str]) -> list[str]:
    """进阶版：with 语句自动关闭文件，并且逐行迭代。"""
    with file_path.open(mode='w', encoding='utf-8') as f:  # with 块结束后自动 close
        f.writelines(line + '\n' for line in lines)  # 生成器表达式，不额外创建列表

    with file_path.open(mode='r', encoding='utf-8') as f:
        # 文件对象本身就是可迭代的，每次只读一行，rstrip 去掉行尾换行符
        return [line.rstrip('\n') for line in f]


def append_and_count_lines(file_path: Path, new_lines: list[str]) -> int:
    """追加写入后统计总行数：模式 'a' 不会覆盖旧内容，适合日志增量写入。"""
    with file_path.open(mode='a', encoding='utf-8') as f:  # 追加模式
        for line in new_lines:
            f.write(line + '\n')

    total = 0  # 注意：不用 sum/count 这类内置名作变量名
    with file_path.open(mode='r', encoding='utf-8') as f:
        for _ in f:  # 流式遍历，每次只持有一行，内存占用恒定
            total += 1
    return total


def read_or_default(file_path: Path, default: str = '') -> str:
    """文件不存在时返回默认值，而不是让程序崩溃（异常处理的常见用法）。"""
    try:
        return file_path.read_text(encoding='utf-8')  # pathlib 的一行读取写法
    except FileNotFoundError:  # 只捕获“文件不存在”这一种明确错误
        return default


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    with tempfile.TemporaryDirectory() as tmp_dir:  # 临时目录，测试结束自动删除，不污染仓库
        base = Path(tmp_dir)

        # 1. 直观版与 with 版读写结果一致
        basic_path = base / 'basic.txt'
        assert write_read_basic(basic_path, ['苹果', 'Apple', '']) == '苹果\nApple\n\n'

        with_path = base / 'with.txt'
        assert write_read_with(with_path, ['苹果', 'Apple', '']) == ['苹果', 'Apple', '']

        # 2. 追加写入：先写 2 行，再追加 3 行，总数应为 5
        log_path = base / 'log.txt'
        write_read_with(log_path, ['第一行', '第二行'])
        assert append_and_count_lines(log_path, ['第三行', '第四行', '第五行']) == 5

        # 3. 边界：空文件统计为 0 行
        empty_path = base / 'empty.txt'
        empty_path.write_text('', encoding='utf-8')
        assert append_and_count_lines(empty_path, []) == 0

        # 4. 不存在的文件返回默认值
        assert read_or_default(base / 'not_exist.txt', default='缺省') == '缺省'
        assert read_or_default(basic_path) == '苹果\nApple\n\n'

    print('✅ 文件读写所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 文件读写与路径处理 {'*' * 12}", sep='', end='\n\n')
    with tempfile.TemporaryDirectory() as tmp_dir:
        demo_path = Path(tmp_dir) / 'demo.txt'
        lines = write_read_with(demo_path, ['第一行：Hello', '第二行：你好', '第三行：Python'])
        for index, line in enumerate(lines, start=1):  # enumerate 同时拿到序号和内容
            print(f'第 {index} 行 -> {line}')

        total = append_and_count_lines(demo_path, ['第四行：追加的数据'])
        print(f'追加后文件总行数: {total}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
