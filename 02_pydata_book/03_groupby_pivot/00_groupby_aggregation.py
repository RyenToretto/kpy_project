"""
[主题]: 分组聚合 (groupby / agg / transform / pivot_table)
[来源]: wesm/pydata-book 第 10 章「数据聚合与分组运算」(本文件为自行重写的学习版)
[难度]: Medium
[前置知识]: 02_pydata_book/01_pandas_structures、02_cleaning (清洗后的数据)

一、主题说明
“按某一列分组，再对每组做统计”是数据分析最常见的操作，对应 SQL 的 GROUP BY。
- groupby(...).agg(...): 每组得到一个汇总值（如总额、平均值）。
- groupby(...).transform(...): 每组的结果会广播回原表的每一行（如组内排名、组内占比）。
- pivot_table: 把“行 × 列”的交叉统计展开成二维表，便于阅读与画图。

二、解法对比（以「每个城市的订单总额」为例）
1. 直观版 total_by_city_loop: 用字典手动累加，逐行遍历。
   - 时间复杂度 O(N)，空间复杂度 O(城市数)
2. 进阶版 total_by_city_groupby: groupby + agg，一行完成多个统计量。
   - 时间复杂度 O(N log N)（内部排序）或 O(N)（哈希分组），空间复杂度 O(N)
3. 组内运算版 add_share_within_city: groupby + transform，给每一行加上“占本城市总额的比例”。
   - 时间复杂度 O(N)，空间复杂度 O(N)

三、真实用途
- 大数据: Spark 的 groupBy / agg 与 Pandas 写法几乎一致，掌握后迁移成本很低。
- 数据分析: 销售日报、用户分层、渠道对比，都是分组聚合 + 透视。
- AI Agent / RAG: 评测结果按问题类型分组，统计各类问题的命中率与平均得分。
- 全栈开发: 后台报表的汇总接口，本质就是 SQL GROUP BY 或 Pandas groupby。
"""

from __future__ import annotations

import pandas as pd


def build_orders() -> pd.DataFrame:
    """构造一份模拟订单表（已完成清洗的数据），便于离线演示。"""
    return pd.DataFrame(
        {
            'city': ['长沙', '长沙', '武汉', '武汉', '长沙', '广州'],
            'channel': ['线上', '线下', '线上', '线上', '线上', '线下'],
            'amount': [100.0, 200.0, 50.0, 150.0, 300.0, 80.0],
        }
    )


def total_by_city_loop(df: pd.DataFrame) -> dict[str, float]:
    """直观版：逐行遍历，手动把金额累加到对应城市。"""
    totals: dict[str, float] = {}
    for city, amount in zip(df['city'], df['amount'], strict=True):  # strict=True 长度不一致时报错
        totals[city] = totals.get(city, 0.0) + amount
    return totals


def total_by_city_groupby(df: pd.DataFrame) -> pd.DataFrame:
    """进阶版：一次性得到总额、订单数与平均金额，列名清楚。"""
    return df.groupby('city').agg(
        total_amount=('amount', 'sum'),
        order_count=('amount', 'count'),
        avg_amount=('amount', 'mean'),
    )


def add_share_within_city(df: pd.DataFrame) -> pd.DataFrame:
    """transform: 每个城市内部的金额占比，结果与原表行数一致，可以直接加成新列。"""
    result = df.copy()
    city_total = result.groupby('city')['amount'].transform('sum')  # 每一行对应所在城市的总额
    result['share_in_city'] = result['amount'] / city_total
    return result


def channel_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """透视表: 行是城市，列是渠道，值是金额总和；缺失组合用 0 填充。"""
    return pd.pivot_table(
        df,
        index='city',
        columns='channel',
        values='amount',
        aggfunc='sum',
        fill_value=0.0,
    )


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    df = build_orders()

    # 1. 直观版与 groupby 结果一致
    loop_totals = total_by_city_loop(df)
    assert loop_totals == {'长沙': 600.0, '武汉': 200.0, '广州': 80.0}

    summary = total_by_city_groupby(df)
    assert summary.loc['长沙', 'total_amount'] == 600.0
    assert summary.loc['长沙', 'order_count'] == 3
    assert summary.loc['武汉', 'avg_amount'] == 100.0
    for city, total in loop_totals.items():
        assert summary.loc[city, 'total_amount'] == total

    # 2. transform: 行数不变，每个城市内部占比之和为 1
    shared = add_share_within_city(df)
    assert len(shared) == len(df)
    per_city_share = shared.groupby('city')['share_in_city'].sum()
    assert (per_city_share - 1.0).abs().max() < 1e-9
    assert shared.loc[0, 'share_in_city'] == 100.0 / 600.0  # 第一行：100 / 长沙总额 600

    # 3. 透视表: 武汉没有线下订单，应被填充为 0
    pivot = channel_pivot(df)
    assert pivot.loc['武汉', '线下'] == 0.0
    assert pivot.loc['长沙', '线上'] == 400.0  # 100 + 300

    # 4. 边界：空 DataFrame 分组后结果为空
    empty = df.iloc[0:0]
    assert total_by_city_groupby(empty).empty

    print('✅ 分组聚合与透视表所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 分组聚合与透视表 {'*' * 12}", sep='', end='\n\n')
    df = build_orders()
    print('按城市汇总:')
    print(total_by_city_groupby(df))
    print('\n城市内占比:')
    print(add_share_within_city(df))
    print('\n城市 × 渠道 透视:')
    print(channel_pivot(df))
    run_tests()


if __name__ == '__main__':
    bootstrap()
