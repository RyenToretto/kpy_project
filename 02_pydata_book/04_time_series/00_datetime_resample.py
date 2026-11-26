"""
[主题]: 时间序列处理 (to_datetime / 索引切片 / resample 重采样 / rolling 滚动 / pct_change 环比)
[来源]: wesm/pydata-book 第 11 章「时间序列」(本文件为自行重写的学习版)
[难度]: Medium
[前置知识]: 03_groupby_pivot (分组聚合)、02_cleaning (日期字符串清洗)

一、主题说明
业务数据大多带时间：订单时间、埋点时间、股价、服务器指标。时间序列分析常见的三件事：
- 把字符串变成真正的时间类型，才能比较、排序、切片；
- 重采样: 把日数据汇总成周/月（降采样），或把低频数据插值成高频（升采样）；
- 滚动与环比: 看趋势而不是看单日噪声（7 日均线、同比与环比增长）。

二、解法对比（以「按月汇总日销售额」为例）
1. 直观版 monthly_total_loop: 手动解析月份字符串，用字典累加。
   - 时间复杂度 O(N)，空间复杂度 O(月份数)
2. 进阶版 monthly_total_resample: 设置 DatetimeIndex 后直接 resample('MS').sum()。
   - 时间复杂度 O(N)，空间复杂度 O(月份数)；缺失月份自动补 0 或 NaN，行为可控。

三、真实用途
- 大数据: 日志、埋点、IoT 数据都按时间分区，重采样是监控大盘的基础。
- 数据分析: 月度/周度经营分析、同比环比，是财务与运营报表的标准动作。
- AI Agent / RAG: 对话与文档的更新时间决定检索时的新鲜度权重，需要按时间筛选。
- 全栈开发: 指标接口的时间粒度（按小时/天/月）切换，本质就是 resample。
"""

from __future__ import annotations

import pandas as pd


def build_daily_sales() -> pd.Series:
    """构造 2024-01-01 ~ 2024-03-31 的模拟日销售额（共 91 天），索引为日期。"""
    dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
    # 用确定性的公式生成数据，保证每次运行结果一致，便于断言
    values = [100.0 + (index % 7) * 10.0 for index in range(len(dates))]
    return pd.Series(values, index=dates, name='sales')


def monthly_total_loop(dates: list[str], values: list[float]) -> dict[str, float]:
    """直观版：手动取出“年-月”前缀，再累加到字典里。"""
    totals: dict[str, float] = {}
    for date_text, value in zip(dates, values, strict=True):
        month = date_text[:7]  # '2024-01-15' -> '2024-01'
        totals[month] = totals.get(month, 0.0) + value
    return totals


def monthly_total_resample(sales: pd.Series) -> pd.Series:
    """进阶版：resample('MS') 按月起始日分组汇总；'MS' 表示 Month Start。"""
    return sales.resample('MS').sum()


def seven_day_rolling(sales: pd.Series) -> pd.Series:
    """7 日滚动平均：前 6 天窗口不足，结果为 NaN，min_periods=7 让这一点更明确。"""
    return sales.rolling(window=7, min_periods=7).mean()


def month_over_month(monthly: pd.Series) -> pd.Series:
    """环比增长率：本月相对上月的变化比例，第一个月没有上月，结果为 NaN。"""
    return monthly.pct_change()


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    sales = build_daily_sales()
    assert len(sales) == 91
    assert isinstance(sales.index, pd.DatetimeIndex)  # 索引必须是时间类型，才能按月重采样

    # 1. 直观版与 resample 结果一致（月份字符串对齐）
    dates = [d.strftime('%Y-%m-%d') for d in sales.index]
    loop_totals = monthly_total_loop(dates, sales.tolist())
    monthly = monthly_total_resample(sales)
    assert len(monthly) == 3  # 1、2、3 月
    for timestamp, total in monthly.items():
        assert abs(loop_totals[timestamp.strftime('%Y-%m')] - total) < 1e-9  # 浮点数用容差比较

    # 2. 按标签切片：Pandas 支持用字符串直接切某个月
    jan = sales.loc['2024-01']
    assert len(jan) == 31
    assert abs(jan.sum() - monthly.iloc[0]) < 1e-9

    # 3. 滚动平均：第 7 天才有值，之前都是 NaN
    rolling = seven_day_rolling(sales)
    assert rolling.iloc[:6].isna().all()
    assert not pd.isna(rolling.iloc[6])
    assert abs(rolling.iloc[6] - sales.iloc[:7].mean()) < 1e-9

    # 4. 环比：第一个月是 NaN，第二个月 = 二月 / 一月 - 1
    mom = month_over_month(monthly)
    assert pd.isna(mom.iloc[0])
    assert abs(mom.iloc[1] - (monthly.iloc[1] / monthly.iloc[0] - 1)) < 1e-12

    # 5. 边界：空序列重采样后为空
    empty = pd.Series([], dtype=float, index=pd.DatetimeIndex([]))
    assert monthly_total_resample(empty).empty

    print('✅ 时间序列处理所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 时间序列处理 {'*' * 12}", sep='', end='\n\n')
    sales = build_daily_sales()
    print('前 3 天销售额:')
    print(sales.head(3))
    print('\n按月汇总:')
    monthly = monthly_total_resample(sales)
    print(monthly)
    print('\n环比增长:')
    print(month_over_month(monthly))
    run_tests()


if __name__ == '__main__':
    bootstrap()
