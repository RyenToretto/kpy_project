"""
[主题]: 自然语言转 SQL (Text2SQL) 与查询重构 (同义词归一化 / 参数化 / 只读安全校验)
[来源]: datawhalechina/all-in-rag 第四章「Text2SQL 与查询重构」(本文件为自行重写的标准库学习版，规则代替大模型)
[难度]: Hard
[前置知识]: 01_python_100_days/02_sqlite_database (sqlite3 与参数化查询)、正则表达式、集合

一、主题说明
业务人员习惯用中文提问“长沙的销售额是多少”，数据库只认 SQL。Text2SQL 就是中间那层翻译，分三步：
1. 查询重构: 把口语与同义词统一成标准词（“营收”“金额” -> “销售额”），让后面的映射更稳；
2. 意图到 SQL: 识别问题想要什么（总额、订单数、平均值、分组排名），生成对应语句；
3. 安全执行: 只允许只读的 SELECT，只能访问白名单里的表，城市等条件用参数占位符传入。
真实系统中第 2 步通常由大模型完成，并会在执行前用结构化 Schema 约束它。这里用规则表代替模型，便于看清每一步。

二、解法对比（以「把问题变成可执行的 SQL」为例）
1. 直观版 naive_to_sql: 直接把问题字符串拼进 SQL。既不安全，也无法处理同义词。
   - 时间复杂度 O(问题长度)，存在 SQL 注入风险（反面教材）。
2. 进阶版 question_to_sql + is_safe_sql: 先重构查询，再按意图生成参数化 SQL，执行前做安全校验。
   - 时间复杂度 O(规则数 × 问题长度)，空间复杂度 O(1)，可以安全地暴露给业务人员使用。

三、真实用途
- 大数据: 让非技术人员直接查询数仓，减少数据团队的临时取数工作量。
- 数据分析: 报表自助查询、指标口径统一，都依赖“同义词 -> 标准字段”的映射表。
- AI Agent / RAG: Agent 访问数据库时，必须限制为只读、白名单表，这是企业落地的安全底线。
- 全栈开发: 后台的“高级筛选”功能本质就是受限的 Text2SQL，参数化与白名单是必做项。
"""

from __future__ import annotations

import re
import sqlite3

# 同义词表：长的词优先替换，避免“销售额”被部分替换
SYNONYMS: dict[str, str] = {
    '营收': '销售额',
    '金额': '销售额',
    '地区': '城市',
    '单数': '订单数',
}

CITIES = ['长沙', '武汉', '广州']
ALLOWED_TABLES = {'SALES'}  # 白名单：只允许访问这些表（大写比较）
FORBIDDEN_KEYWORDS = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'PRAGMA', 'ATTACH', 'CREATE', 'REPLACE'}


def build_demo_db() -> sqlite3.Connection:
    """构造一个内存数据库，包含销售明细表 sales，方便离线演示。"""
    conn = sqlite3.connect(':memory:')
    conn.execute(
        'CREATE TABLE sales (order_id INTEGER, city TEXT, product TEXT, amount REAL, order_date TEXT)'
    )
    rows = [
        (1, '长沙', '咖啡', 100.0, '2026-01-03'),
        (2, '长沙', '茶', 50.0, '2026-01-05'),
        (3, '武汉', '咖啡', 80.0, '2026-02-01'),
        (4, '广州', '茶', 120.0, '2026-02-10'),
        (5, '长沙', '咖啡', 60.0, '2026-03-01'),
    ]
    conn.executemany('INSERT INTO sales VALUES (?, ?, ?, ?, ?)', rows)
    conn.commit()
    return conn


def rewrite_query(question: str) -> str:
    """查询重构：把同义词统一替换为标准词，返回归一化后的问题。"""
    normalized = question
    for synonym in sorted(SYNONYMS, key=len, reverse=True):  # 长词优先
        normalized = normalized.replace(synonym, SYNONYMS[synonym])
    return normalized


def question_to_sql(question: str) -> tuple[str, tuple[object, ...]] | None:
    """意图识别并生成参数化 SQL。无法识别时返回 None，而不是硬猜一条语句。"""
    q = rewrite_query(question)
    city = next((c for c in CITIES if c in q), None)  # 问题里提到的城市（如果有）
    if '按城市' in q and '销售额' in q:
        return ('SELECT city, SUM(amount) AS total FROM sales GROUP BY city ORDER BY total DESC', ())
    if '平均' in q and city:
        return ('SELECT AVG(amount) FROM sales WHERE city = ?', (city,))
    if '订单数' in q and city:
        return ('SELECT COUNT(*) FROM sales WHERE city = ?', (city,))
    if '销售额' in q and city:
        return ('SELECT SUM(amount) FROM sales WHERE city = ?', (city,))
    if '订单数' in q:
        return ('SELECT COUNT(*) FROM sales', ())
    return None


def is_safe_sql(sql: str) -> bool:
    """安全校验：只允许一条只读 SELECT，且只访问白名单中的表。"""
    stripped = sql.strip().rstrip(';').strip()
    if ';' in stripped:  # 不允许多条语句拼接执行
        return False
    tokens = re.findall(r'[A-Za-z_]+', stripped.upper())
    if not tokens or tokens[0] != 'SELECT':
        return False
    if FORBIDDEN_KEYWORDS & set(tokens):  # 出现写操作关键字直接拒绝
        return False
    if 'FROM' in tokens:
        table = tokens[tokens.index('FROM') + 1]
        return table in ALLOWED_TABLES
    return True


def execute_question(conn: sqlite3.Connection, question: str) -> list[tuple[object, ...]] | None:
    """完整流程：问题 -> SQL -> 安全校验 -> 参数化执行。无法识别时返回 None。"""
    built = question_to_sql(question)
    if built is None:
        return None
    sql, params = built
    if not is_safe_sql(sql):  # 双保险：生成的语句也要过一遍安全校验
        raise PermissionError(f'拒绝执行不安全的 SQL: {sql}')
    return conn.execute(sql, params).fetchall()


def run_tests() -> None:
    """自动化断言测试：覆盖查询重构、各类意图、安全拦截与无法识别的问题。"""
    conn = build_demo_db()

    # 1. 查询重构：同义词被统一替换
    assert rewrite_query('营收按城市统计') == '销售额按城市统计'
    assert rewrite_query('长沙金额') == '长沙销售额'

    # 2. 分组排名：按城市汇总销售额，并按总额降序
    grouped = execute_question(conn, '按城市统计销售额')
    assert grouped == [('长沙', 210.0), ('广州', 120.0), ('武汉', 80.0)]

    # 3. 单城市指标：总额、订单数、平均值
    assert execute_question(conn, '武汉的销售额') == [(80.0,)]
    assert execute_question(conn, '长沙的订单数') == [(3,)]
    assert execute_question(conn, '长沙平均营收') == [(70.0,)]  # 同义词 营收 -> 销售额

    # 4. 全表订单数
    assert execute_question(conn, '总订单数') == [(5,)]

    # 5. 安全拦截：写操作、多语句、非白名单表都会被拒绝
    assert is_safe_sql('SELECT amount FROM sales') is True
    assert is_safe_sql('DROP TABLE sales') is False
    assert is_safe_sql('SELECT * FROM sales; DROP TABLE sales') is False
    assert is_safe_sql('SELECT * FROM users') is False
    assert is_safe_sql('DELETE FROM sales') is False

    # 6. 无法识别的问题返回 None，而不是乱猜 SQL
    assert execute_question(conn, '今天天气怎么样') is None

    conn.close()
    print('✅ Text2SQL 与查询重构所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 自然语言转 SQL {'*' * 12}", sep='', end='\n\n')
    conn = build_demo_db()
    for question in ['按城市统计销售额', '长沙的订单数', '长沙平均营收', '今天天气怎么样']:
        built = question_to_sql(question)
        result = execute_question(conn, question)
        print(f'问题: {question}')
        print(f'  重构后: {rewrite_query(question)}')
        print(f'  SQL: {built[0] if built else "（无法识别）"}  结果: {result}')
    conn.close()
    run_tests()


if __name__ == '__main__':
    bootstrap()
