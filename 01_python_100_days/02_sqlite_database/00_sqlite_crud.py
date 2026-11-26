"""
[主题]: SQLite 数据库增删改查 (sqlite3 标准库 + 参数化查询)
[来源]: jackfrued/Python-100-Days 第 40~45 天「数据库编程」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 01_python_100_days/01_json_and_csv (数据读写)、元组/列表、异常处理

一、主题说明
- SQLite 是随 Python 自带的轻量数据库，一个文件就是一个库，适合学习、原型与小型应用。
- 所有 SQL 都要用 ? 占位符传参，绝不用 f-string 拼接用户输入，否则会被 SQL 注入攻击。
- 连接对象 with 结束时只提交/回滚事务，不会自动 close，所以要显式 close 或用 contextlib.closing。

二、解法对比
1. 直观版 find_user_unsafe: f-string 拼接 SQL。遇到 "' OR '1'='1" 这类输入会泄露全部数据（反面教材）。
   - 时间复杂度 取决于数据库索引，空间复杂度 O(结果行数)
2. 进阶版 find_user: 使用 ? 占位符，驱动会自动转义参数。
   - 时间复杂度 有索引时 O(log N)，无索引时 O(N)；空间复杂度 O(结果行数)
3. 批量写入 insert_many: executemany 一次提交多行，比循环 execute 更快。
   - 时间复杂度 O(N)，但事务只提交一次，减少磁盘同步次数。

三、真实用途
- 大数据: 本地小规模中间结果、去重表、任务状态表常用 SQLite 暂存。
- 数据分析: 把 CSV 导入 SQLite 后用 SQL 做分组统计，是数据分析入门的第一站。
- AI Agent / RAG: 对话历史、文档元数据、向量之外的结构化信息都可以存在 SQLite。
- 全栈开发: 小型 Web 应用（如个人博客、工具站）的默认数据库；参数化查询是防注入的底线。
"""

from __future__ import annotations

import sqlite3
from contextlib import closing


def create_table(conn: sqlite3.Connection) -> None:
    """建表：id 自增主键，name 不能为空，email 唯一。"""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增主键
            name  TEXT NOT NULL,                      -- 姓名，不允许为空
            email TEXT UNIQUE,                        -- 邮箱，不允许重复
            age   INTEGER
        )
        """
    )
    conn.commit()  # DDL 也要提交才会真正生效


def insert_user(conn: sqlite3.Connection, name: str, email: str, age: int) -> int:
    """插入一条用户并返回新生成的 id。"""
    cursor = conn.execute(
        'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',  # ? 是占位符
        (name, email, age),  # 参数单独传入，驱动会自动转义
    )
    conn.commit()
    return cursor.lastrowid or 0


def insert_many(conn: sqlite3.Connection, rows: list[tuple[str, str, int]]) -> int:
    """批量插入：executemany 复用同一条 SQL，一次事务提交。"""
    conn.executemany(
        'INSERT INTO users (name, email, age) VALUES (?, ?, ?)',
        rows,
    )
    conn.commit()
    return len(rows)


def find_user_unsafe(conn: sqlite3.Connection, name: str) -> list[tuple]:
    """反面教材：f-string 拼接 SQL，输入 "' OR '1'='1" 会返回全部用户。"""
    sql = f"SELECT id, name, email, age FROM users WHERE name = '{name}'"  # 危险！
    return conn.execute(sql).fetchall()


def find_user(conn: sqlite3.Connection, name: str) -> list[tuple]:
    """安全查询：参数化占位符，输入内容只会被当作普通字符串。"""
    cursor = conn.execute(
        'SELECT id, name, email, age FROM users WHERE name = ?',
        (name,),
    )
    return cursor.fetchall()


def update_age(conn: sqlite3.Connection, user_id: int, new_age: int) -> int:
    """更新年龄，返回受影响的行数（0 表示没有这个用户）。"""
    cursor = conn.execute('UPDATE users SET age = ? WHERE id = ?', (new_age, user_id))
    conn.commit()
    return cursor.rowcount


def delete_user(conn: sqlite3.Connection, user_id: int) -> int:
    """删除用户，返回受影响的行数。"""
    cursor = conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    return cursor.rowcount


def average_age(conn: sqlite3.Connection) -> float:
    """用 SQL 聚合函数统计平均年龄；没有数据时返回 0.0。"""
    row = conn.execute('SELECT AVG(age) FROM users').fetchone()
    return float(row[0]) if row and row[0] is not None else 0.0


def run_tests() -> None:
    """自动化断言测试：使用内存数据库 ':memory:'，测试结束即销毁，不留文件。"""
    with closing(sqlite3.connect(':memory:')) as conn:
        create_table(conn)
        assert average_age(conn) == 0.0  # 边界：空表的平均年龄

        first_id = insert_user(conn, '张三', 'zhangsan@example.com', 20)
        assert first_id == 1
        assert insert_many(conn, [('李四', 'lisi@example.com', 30), ('王五', 'wangwu@example.com', 40)]) == 2

        # 1. 参数化查询能正确找到用户
        assert find_user(conn, '李四') == [(2, '李四', 'lisi@example.com', 30)]

        # 2. 不安全写法会被注入，返回全部 3 个用户；安全写法不会
        injected = "' OR '1'='1"
        assert len(find_user_unsafe(conn, injected)) == 3
        assert find_user(conn, injected) == []

        # 3. 更新与删除：返回的 rowcount 可以判断是否真的命中
        assert update_age(conn, 1, 21) == 1
        assert update_age(conn, 999, 1) == 0  # 不存在的 id 不会报错，只是影响 0 行
        assert delete_user(conn, 3) == 1
        assert find_user(conn, '王五') == []

        # 4. 聚合：平均年龄 = (21 + 30) / 2 = 25.5
        assert average_age(conn) == 25.5

        # 5. UNIQUE 约束：重复邮箱会抛出 IntegrityError，需要用异常处理
        try:
            insert_user(conn, '重复', 'zhangsan@example.com', 1)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError('重复邮箱必须被 UNIQUE 约束拒绝')

    print('✅ SQLite 增删改查所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} SQLite 数据库增删改查 {'*' * 12}", sep='', end='\n\n')
    with closing(sqlite3.connect(':memory:')) as conn:
        create_table(conn)
        insert_many(conn, [('张三', 'a@example.com', 20), ('李四', 'b@example.com', 30)])
        print('查询 张三:', find_user(conn, '张三'))
        print('平均年龄:', average_age(conn))
    run_tests()


if __name__ == '__main__':
    bootstrap()
