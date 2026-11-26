"""
[主题]: 数据读取与清洗 (read_csv / 缺失值 / 重复行 / 类型转换 / 字符串清洗)
[来源]: wesm/pydata-book 第 6~7 章「数据加载」「数据清洗与准备」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 01_pandas_structures (DataFrame 基础)、字符串方法

一、主题说明
真实数据几乎都是脏的：空值、重复行、数字写成了字符串、多余空格、大小写不统一。
清洗的目标是让每一列的类型、取值范围都符合预期，再进入分析。
本文件用一段带“脏数据”的 CSV 演示完整流程，数据全部内置在代码里，离线可运行。

二、解法对比（以「清洗订单金额」为例）
1. 直观版 clean_rows_loop: 逐行判断、手动 float 转换，缺失值用 if 跳过。
   - 时间复杂度 O(N)，空间复杂度 O(N)
2. 进阶版 clean_dataframe: 使用 pd.to_numeric(errors='coerce') 把非法值变成 NaN，再统一填充与去重。
   - 时间复杂度 O(N)（向量化），空间复杂度 O(N)

三、真实用途
- 大数据: 上游埋点、日志常有缺字段与重复上报，清洗规则决定了下游指标是否可信。
- 数据分析: 财务与销售报表在汇总前必须去重、统一金额单位与日期格式。
- AI Agent / RAG: 知识库文档入库前要去重、去空白、过滤空文本，否则检索会出现重复答案。
- 全栈开发: 用户提交的表单数据要先规范化（去空格、转类型）再入库。
"""

from __future__ import annotations

from io import StringIO

import pandas as pd

RAW_CSV = """order_id,customer,amount,city
1001, 张三 ,128.5,长沙
1002,李四,,武汉
1003,王五,99,长沙
1001, 张三 ,128.5,长沙
1004,赵六,abc,广州
1005,钱七,58.0,
"""


def clean_rows_loop(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    """直观版：逐行处理。金额无法转换或为空的行直接丢弃，并手动去除首尾空格。"""
    cleaned: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    for row in rows:
        order_id = row['order_id'].strip()
        if order_id in seen_ids:  # 手动去重：记录已经见过的订单号
            continue
        seen_ids.add(order_id)
        try:
            amount = float(row['amount'])  # 空字符串或 'abc' 会抛出 ValueError
        except ValueError:
            continue  # 金额非法，丢弃该行
        cleaned.append({
            'order_id': order_id,
            'customer': row['customer'].strip(),
            'amount': amount,
            'city': row['city'].strip() or '未知',
        })
    return cleaned


def load_raw() -> pd.DataFrame:
    """读取 CSV 字符串：StringIO 把字符串包装成“文件”，无需真的写磁盘。"""
    return pd.read_csv(StringIO(RAW_CSV), dtype={'order_id': str})  # 订单号保持字符串，避免丢失前导零


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """进阶版：向量化清洗，每一步都返回新的 DataFrame，不修改原数据。"""
    result = df.copy()
    # 1. 字符串清洗：去除首尾空格
    result['customer'] = result['customer'].str.strip()
    # 2. 类型转换：无法转换的值变成 NaN，而不是直接报错
    result['amount'] = pd.to_numeric(result['amount'], errors='coerce')
    # 3. 缺失值处理：城市缺失填 '未知'，金额缺失的行直接删除
    result['city'] = result['city'].fillna('未知')
    result = result.dropna(subset=['amount'])
    # 4. 去重：同一订单号只保留第一次出现的记录
    result = result.drop_duplicates(subset=['order_id'], keep='first')
    return result.reset_index(drop=True)  # 重置行索引，让结果从 0 连续编号


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例、脏数据与边界用例。"""
    raw = load_raw()
    assert raw.shape == (6, 4)  # 表头 + 6 行数据（含重复、缺失、非法值）

    # 1. 进阶版清洗结果：只保留金额合法且订单号不重复的记录
    cleaned = clean_dataframe(raw)
    assert cleaned['order_id'].tolist() == ['1001', '1003', '1005']
    assert cleaned['customer'].tolist() == ['张三', '王五', '钱七']  # 空格已去掉
    assert cleaned['city'].tolist() == ['长沙', '长沙', '未知']  # 缺失城市被填充
    assert cleaned['amount'].sum() == 128.5 + 99 + 58.0

    # 2. 直观版与向量化版的订单号结果一致
    rows = raw.fillna('').astype(str).to_dict(orient='records')
    loop_result = clean_rows_loop(rows)
    assert [item['order_id'] for item in loop_result] == cleaned['order_id'].tolist()

    # 3. 边界：没有任何数据行时清洗结果为空（用 iloc 截取空表，保留原始列类型）
    assert clean_dataframe(raw.iloc[0:0]).empty

    # 4. 原始数据不被修改（copy 的意义）
    assert raw['customer'].iloc[0] == ' 张三 '

    print('✅ 数据读取与清洗所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 数据读取与清洗 {'*' * 12}", sep='', end='\n\n')
    raw = load_raw()
    print('原始数据:')
    print(raw)
    print('\n清洗后数据:')
    print(clean_dataframe(raw))
    run_tests()


if __name__ == '__main__':
    bootstrap()
