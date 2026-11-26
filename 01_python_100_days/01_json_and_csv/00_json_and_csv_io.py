"""
[主题]: JSON 与 CSV 数据读写 (json / csv 标准库)
[来源]: jackfrued/Python-100-Days 第 22~23 天「JSON 与 CSV」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 00_basic 语法主线、字典/列表、文件读写 (01_python_100_days/00_file_io)

一、主题说明
- JSON: 键值结构的通用数据格式，接口、配置文件、大模型工具调用的参数基本都是它。
- CSV : 表格数据的通用格式，Excel / 数据库导出 / Pandas 读取都以它为入口。
- 注意 CSV 字段里可能含逗号、引号、换行，手写 split(',') 会出错，必须用 csv 模块。

二、解法对比
1. JSON 直观版 save_json_basic: json.dumps 直接写入字符串（中文会被转成 \\uXXXX 转义）。
   - 时间复杂度 O(数据大小)，空间复杂度 O(数据大小)
2. JSON 进阶版 save_json: ensure_ascii=False 保留中文，indent 让文件可读，文件对象直接 dump。
   - 时间复杂度 O(数据大小)，空间复杂度 O(数据大小)
3. CSV 直观版 parse_csv_naive: 按逗号 split，遇到 "Hello, World" 这类带逗号字段就会错位。
   - 时间复杂度 O(行数 * 列数)
4. CSV 进阶版 read_csv_rows: csv.DictReader 自动处理引号与转义，每行变成字典。
   - 时间复杂度 O(行数 * 列数)，空间复杂度 O(行数 * 列数)

三、真实用途
- 大数据: 日志和中间结果常以 JSON Lines / CSV 落盘，是 Spark、Pandas 的常见输入。
- 数据分析: 业务导出的 CSV 报表是最常见的分析原料。
- AI Agent / RAG: 大模型的工具调用参数、评测集（question/answer 对）都是 JSON。
- 全栈开发: 接口返回 JSON，前后端之间的数据契约就是它。
"""

from __future__ import annotations

import csv
import json
import tempfile
from pathlib import Path
from typing import Any


def save_json_basic(data: dict[str, Any]) -> str:
    """直观版：返回 JSON 字符串。中文会被转义成 \\uXXXX，人眼难读。"""
    return json.dumps(data)  # 默认 ensure_ascii=True，中文会变成转义序列


def save_json(file_path: Path, data: dict[str, Any]) -> None:
    """进阶版：保留中文、缩进 2 格，直接写入文件。"""
    with file_path.open(mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)  # 中文原样保存，便于人工检查


def load_json(file_path: Path) -> dict[str, Any]:
    """读取 JSON 文件并还原为 Python 字典/列表。"""
    with file_path.open(mode='r', encoding='utf-8') as f:
        return json.load(f)


def parse_csv_naive(line: str) -> list[str]:
    """直观版：用 split 切分一行 CSV。遇到带引号的逗号会错位（反面教材）。"""
    return line.split(',')


def write_csv(file_path: Path, rows: list[dict[str, str]]) -> None:
    """用 DictWriter 写 CSV：字段名取自第一行字典的键，含逗号的值会自动加引号。"""
    if not rows:  # 边界：没有数据时直接返回，避免读取 rows[0] 报错
        return
    headers = list(rows[0].keys())  # 表头 = 字典的键
    with file_path.open(mode='w', encoding='utf-8', newline='') as f:  # newline='' 防止 Windows 多出空行
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()  # 先写表头
        writer.writerows(rows)  # 再批量写数据行


def read_csv_rows(file_path: Path) -> list[dict[str, str]]:
    """进阶版：DictReader 自动处理引号与转义，每一行都是一个字典。"""
    with file_path.open(mode='r', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))  # 所有值都是字符串，需要数字时自行转换


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    # 1. JSON：直观版会转义中文，进阶版保留中文
    sample = {'name': '张三', 'age': 18}
    assert '\\u' in save_json_basic(sample)  # 直观版：中文被转义
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)

        json_path = base / 'user.json'
        save_json(json_path, sample)
        assert '张三' in json_path.read_text(encoding='utf-8')  # 进阶版：中文原样保存
        assert load_json(json_path) == sample  # 往返读写数据不变

        # 2. CSV：带逗号的字段，naive 切分会错位，csv 模块正确
        line = '1,"Hello, World",99'
        assert parse_csv_naive(line) == ['1', '"Hello', ' World"', '99']  # 错位的反面教材
        assert len(parse_csv_naive(line)) == 4  # 本应 3 列，切出了 4 列

        csv_path = base / 'books.csv'
        rows = [
            {'id': '1', 'title': 'Hello, World', 'price': '99'},
            {'id': '2', 'title': 'Python 入门', 'price': '59'},
        ]
        write_csv(csv_path, rows)
        assert read_csv_rows(csv_path) == rows  # 往返读写后字段完全一致

        # 3. 边界：空数据写入不报错，也不生成内容
        empty_path = base / 'empty.csv'
        write_csv(empty_path, [])
        assert not empty_path.exists()

    print('✅ JSON 与 CSV 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} JSON 与 CSV 数据读写 {'*' * 12}", sep='', end='\n\n')
    user = {'name': '张三', 'skills': ['Python', 'SQL'], 'active': True}
    print('直观版 JSON（中文被转义）:', save_json_basic(user))

    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        save_json(base / 'user.json', user)
        print('进阶版 JSON 读回:', load_json(base / 'user.json'))

        rows = [{'id': '1', 'title': 'Hello, World'}]
        write_csv(base / 'demo.csv', rows)
        print('CSV 读回（带逗号字段仍正确）:', read_csv_rows(base / 'demo.csv'))
    run_tests()


if __name__ == '__main__':
    bootstrap()
