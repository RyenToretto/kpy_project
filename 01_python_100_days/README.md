# 01_python_100_days | Python-100-Days 中文路线（阶段 2 · 工程与数据底座）

- **原仓库**: [jackfrued/Python-100-Days](https://github.com/jackfrued/python-100-days)（中文 100 天 Python 教程）
- **学习阶段**: 第 2 阶段（`00_leetcode` 之后）
- **建议学习范围**: 原课程 Day 20 ~ 45（异常、文件、JSON/CSV、数据库）。本目录先覆盖这一段的核心，其余章节按需补充。
- **前置语法**: `00_basic/chapter01_hello` ~ `00_basic/chapter05_match`，以及 `00_leetcode` 的列表、字典、循环练习
- **为什么学它（通向大数据 / AI / 全栈）**: 把「会写语法」变成「会读写数据、会处理错误、会存数据库」，这是几乎所有数据与后端岗位的入门门槛。

## 版权与写法说明

本目录的脚本**不是**原课程代码的拷贝，而是按知识点用自己的话重写的学习版，每个脚本都有 `run_tests()` 自测，离线即可运行，不依赖网络与账号。想看原文讲解，请直接访问上面的原仓库。

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应原课程 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_file_io/` | Day 21 文件读写 | `open`/`with`、`pathlib`、追加写入、流式读取 | `00_text_file_read_write.py` | ✅ |
| 01 | `01_json_and_csv/` | Day 22 ~ 23 JSON 与 CSV | `json.dump`/`load`、`csv.DictReader`/`DictWriter`、为什么不能手写 `split(',')` | `00_json_and_csv_io.py` | ✅ |
| 02 | `02_sqlite_database/` | Day 40 ~ 45 数据库 | `sqlite3` 增删改查、参数化查询防注入、`executemany`、聚合 | `00_sqlite_crud.py` | ✅ |
| 03 | `03_exceptions/` | Day 20 异常处理 | `try/except/else/finally`、自定义异常、有上限的重试 | `00_exception_handling.py` | ✅ |

## 学习循环

1. 先读脚本顶部的 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 运行一次：`.venv/bin/python 01_python_100_days/00_file_io/00_text_file_read_write.py`。
3. 修改输入数据或参数，看 `assert` 是否仍然通过。
4. 合上脚本，凭记忆重写一遍。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 01_python_100_days
```

## 后续计划

- Day 46 ~ 60（Web 与爬虫）与 Day 61 之后（数据分析、机器学习）暂不在本阶段生成，数据分析部分由 `02_pydata_book` 覆盖。
