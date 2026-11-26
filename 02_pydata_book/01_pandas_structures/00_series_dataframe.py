"""
[主题]: Pandas 核心数据结构 (Series / DataFrame / 索引 / loc 与 iloc)
[来源]: wesm/pydata-book 第 5 章「Pandas 入门」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 02_pydata_book/00_numpy_basics (ndarray)、字典、列表

一、主题说明
- Series: 带索引的一维数组，可以理解为“有标签的一列”。
- DataFrame: 带行索引和列名的二维表，等价于 Excel 工作表或 SQL 结果集。
- 索引对齐: 两个 Series 相加时，按索引标签对齐，而不是按位置对齐。这是 Pandas 最容易踩坑也最强大的特性。
- loc 按标签取值，iloc 按位置取值。

二、解法对比（以「按城市统计人口」为例）
1. 直观版 population_by_city_loop: 用 dict 和 for 循环手动累加。
   - 时间复杂度 O(N)，空间复杂度 O(城市数)
2. 进阶版 build_dataframe + select_city: DataFrame 直接用 loc 按条件取行。
   - 时间复杂度 O(N)（布尔筛选），空间复杂度 O(N)
3. 对齐版 align_by_index: 两个 Series 按标签相加，缺失的标签自动变成 NaN。
   - 时间复杂度 O(N + M)（哈希对齐），空间复杂度 O(N + M)

三、真实用途
- 大数据: 大规模数据的分片、合并、去重都以 DataFrame 的索引语义为基础。
- 数据分析: 报表里“按部门、按月份”的取数，几乎都是 loc 条件筛选 + 列选择。
- AI Agent / RAG: 评测结果表（问题、召回文档、得分）用 DataFrame 管理最直观。
- 全栈开发: 后台管理的数据导出、统计看板的底层数据处理。
"""

from __future__ import annotations

import pandas as pd


def population_by_city_loop(records: list[tuple[str, int]]) -> dict[str, int]:
    """直观版：用字典手动累加同一城市的人口。"""
    totals: dict[str, int] = {}
    for city, people in records:
        totals[city] = totals.get(city, 0) + people  # 不存在时用 0 作为起点
    return totals


def build_dataframe() -> pd.DataFrame:
    """用字典创建 DataFrame：键是列名，值是该列的数据。"""
    return pd.DataFrame(
        {
            'city': ['长沙', '武汉', '长沙', '广州'],
            'year': [2024, 2024, 2025, 2025],
            'population': [1046, 1373, 1060, 1867],  # 单位：万人
        }
    )


def select_city(df: pd.DataFrame, city: str) -> pd.DataFrame:
    """布尔条件筛选行：df['city'] == city 得到一串 True/False，再用 loc 取出为 True 的行。"""
    return df.loc[df['city'] == city, ['year', 'population']]  # 同时选出需要的列


def align_by_index(first: pd.Series, second: pd.Series) -> pd.Series:
    """索引对齐相加：标签只在一边出现时结果为 NaN，不会串位。"""
    return first + second


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    # 1. 直观版与 DataFrame 的结果一致
    records = [('长沙', 1046), ('武汉', 1373), ('长沙', 1060)]
    totals = population_by_city_loop(records)
    assert totals == {'长沙': 2106, '武汉': 1373}

    df = build_dataframe()
    assert df.shape == (4, 3)
    assert df['population'].sum() == 1046 + 1373 + 1060 + 1867

    # 2. 条件筛选：长沙两年的数据
    changsha = select_city(df, '长沙')
    assert changsha['population'].tolist() == [1046, 1060]
    assert list(changsha.columns) == ['year', 'population']

    # 3. loc 按标签、iloc 按位置，取到的应该是同一行
    assert df.loc[0, 'city'] == df.iloc[0, 0] == '长沙'

    # 4. 索引对齐：只有 'a' 同时存在，其它标签结果为 NaN
    left = pd.Series([1, 2], index=['a', 'b'])
    right = pd.Series([10, 20], index=['b', 'c'])
    result = align_by_index(left, right)
    assert pd.isna(result['a']) and pd.isna(result['c'])  # 只有一边存在 -> NaN
    assert result['b'] == 12  # 两边都存在 -> 左边 2 + 右边 10

    # 边界：空 DataFrame 的行数为 0
    assert len(select_city(df.iloc[0:0], '长沙')) == 0

    print('✅ Pandas 核心结构所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} Pandas 核心数据结构 {'*' * 12}", sep='', end='\n\n')
    df = build_dataframe()
    print(df)
    print('\n长沙的数据:')
    print(select_city(df, '长沙'))
    run_tests()


if __name__ == '__main__':
    bootstrap()
