# 02_pydata_book | 利用 Python 进行数据分析（阶段 2 · 工程与数据底座）

- **原仓库**: [wesm/pydata-book](https://github.com/wesm/pydata-book)（Pandas 作者 Wes McKinney 的官方 Notebook 教材）
- **学习阶段**: 第 2 阶段（与 `01_python_100_days` 同阶段，建议先学 Python-100-Days 的文件与数据库部分）
- **前置语法**: `00_basic/chapter01_hello` ~ `00_basic/chapter05_match`、列表与字典、函数
- **为什么学它（通向大数据 / AI / 全栈）**: NumPy 向量化与 Pandas 清洗、分组、时间序列，是数据分析岗位的核心技能，也是后续 Spark、Polars 与 AI 数据预处理的基础。

## 版权与写法说明

本目录的脚本**不是**原书 Notebook 的拷贝，而是按章节知识点用自己的话重写的学习版，数据全部内置在代码中，离线即可运行。想看原书的完整讲解，请访问上面的原仓库。

## 依赖安装

本目录需要 NumPy 与 Pandas，在项目根目录的 `.venv` 中安装：

```bash
.venv/bin/python -m pip install numpy pandas
```

本次生成时使用的版本：`numpy 2.5.5`、`pandas 3.1.1`。

## 章节与本地文件（顺序学习）

| 序号 | 目录 | 对应原书章节 | 核心知识点 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 00 | `00_numpy_basics/` | 第 4 章 NumPy 基础 | `ndarray`、向量化、布尔索引、广播 | `00_ndarray_vectorization.py` | ✅ |
| 01 | `01_pandas_structures/` | 第 5 章 Pandas 入门 | `Series`、`DataFrame`、`loc`/`iloc`、索引对齐 | `00_series_dataframe.py` | ✅ |
| 02 | `02_cleaning/` | 第 6~7 章 数据加载与清洗 | `read_csv`、缺失值、去重、类型转换、字符串清洗 | `00_missing_duplicates_types.py` | ✅ |
| 03 | `03_groupby_pivot/` | 第 10 章 数据聚合与分组 | `groupby.agg`、`transform`、`pivot_table` | `00_groupby_aggregation.py` | ✅ |
| 04 | `04_time_series/` | 第 11 章 时间序列 | `to_datetime`、`resample`、滚动平均、环比 | `00_datetime_resample.py` | ✅ |

## 学习循环

1. 先读脚本顶部 Docstring，弄清「题目 / 解法对比 / 真实用途」。
2. 运行一次：`.venv/bin/python 02_pydata_book/02_cleaning/00_missing_duplicates_types.py`。
3. 把脚本里的数据换成你自己的 CSV，看清洗结果是否符合预期。
4. 合上脚本，凭记忆重写一遍。

## 验证

```bash
# 验证本目录下全部脚本（导入并执行 run_tests）
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 02_pydata_book
```
