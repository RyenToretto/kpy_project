"""
[主题]: 数据层：版本化迁移、外键级联、事务回滚、参数化查询（SQLModel / Repository 思想的标准库版本）
[来源]: fastapi/full-stack-fastapi-template 的 SQLModel 数据层与 Alembic 迁移思路（本文件为自行重写的 sqlite3 学习版）
[难度]: Medium
[前置知识]: 01_python_100_days/02_sqlite_database (SQLite CRUD)、dataclass、上下文管理器、异常

一、主题说明
全栈后端的数据层要解决四件事：
1. 结构变更可追踪: 用迁移 (migration) 记录每次改表，而不是手改线上数据库；这里用 PRAGMA user_version 记录版本；
2. 关联数据一致: 外键 + ON DELETE CASCADE，删除用户时自动删除他的笔记；
3. 多步操作要么全成功要么全失败: 事务 (transaction)，任一步出错就整体回滚；
4. 防注入: 用户输入只能作为参数传入（? 占位符），绝不能拼接进 SQL 字符串。
SQLModel 把“类 = 表、实例 = 行”的映射自动化了，这里用 dataclass + Repository 手写一遍，理解之后再用 SQLModel 会轻松很多。

二、解法对比（以「按邮箱查用户」为例）
1. 直观版 find_user_unsafe: f-string 拼接 SQL。输入 `' OR '1'='1` 就能拿到所有用户（SQL 注入）。
   - 时间复杂度 O(n)（无索引时全表扫描），安全性为零，仅作反面教材。
2. 进阶版 UserRepo.by_email: 参数化查询 + UNIQUE 索引。
   - 时间复杂度 O(log n)（有 UNIQUE 索引时），输入只被当作数据，不会改变 SQL 结构。

三、真实用途
- 大数据: 元数据表与任务表的版本化迁移，是数据平台上线、回滚的基础。
- 数据分析: 外键保证维度表与事实表的引用完整性，避免报表里出现“孤儿”记录。
- AI Agent / RAG: 会话、消息、文档块、用量统计都存数据库，事务保证“扣费 + 写日志”不会只做一半。
- 全栈开发: 注册用户时同时写用户表和欢迎笔记，任何一步失败都要回滚，这是最常见的线上一致性问题。
"""

from __future__ import annotations

import itertools
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

# 迁移列表：(版本号, SQL)。只能追加，不能修改已发布的迁移，否则线上与本地结构会不一致。
MIGRATIONS: list[tuple[int, str]] = [
    (1, 'CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL)'),
    (2, 'CREATE TABLE notes ('
        'id INTEGER PRIMARY KEY, '
        'user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE, '
        'title TEXT NOT NULL, body TEXT NOT NULL DEFAULT \'\')'),
    (3, 'CREATE INDEX idx_notes_user ON notes(user_id)'),
]


@dataclass
class User:
    """用户模型：对应 users 表的一行。id 为 None 表示尚未入库。"""

    email: str
    name: str
    id: int | None = None


@dataclass
class Note:
    """笔记模型：对应 notes 表的一行，user_id 指向所属用户。"""

    user_id: int
    title: str
    body: str = ''
    id: int | None = None


def connect(path: str = ':memory:') -> sqlite3.Connection:
    """打开连接：开启外键约束（SQLite 默认关闭），并把行返回为可按列名访问的对象。"""
    conn = sqlite3.connect(path)
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    return conn


_savepoint_ids = itertools.count(1)


@contextmanager
def atomic(conn: sqlite3.Connection) -> Iterator[None]:
    """可嵌套的事务块。
    注意：sqlite3 连接自带的 `with conn:` 退出时会直接 COMMIT，嵌套使用会提前提交、撤销不了外层。
    所以这里自己管理：最外层 BEGIN/COMMIT（或 ROLLBACK），内层用 SAVEPOINT 局部回滚。
    """
    if conn.in_transaction:  # 已在事务中：用保存点，内层失败只撤销内层
        name = f'sp_{next(_savepoint_ids)}'
        conn.execute(f'SAVEPOINT {name}')
        try:
            yield
        except BaseException:
            conn.execute(f'ROLLBACK TO {name}')
            conn.execute(f'RELEASE {name}')
            raise
        conn.execute(f'RELEASE {name}')
    else:  # 最外层：开启真正的事务
        conn.execute('BEGIN')
        try:
            yield
        except BaseException:
            conn.rollback()
            raise
        conn.commit()


def migrate(conn: sqlite3.Connection) -> int:
    """按版本号顺序执行尚未应用的迁移，返回最终版本号。重复执行是安全的（幂等）。"""
    current = conn.execute('PRAGMA user_version').fetchone()[0]
    for version, sql in MIGRATIONS:
        if version <= current:
            continue
        with atomic(conn):  # 每个迁移单独一个事务：要么改表并记版本，要么什么都不做
            conn.execute(sql)
            conn.execute(f'PRAGMA user_version = {int(version)}')  # 版本号来自代码常量，不是用户输入
        current = version
    return current


class UserRepo:
    """用户仓库：封装 users 表的增查改删，外部代码不直接写 SQL。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create(self, email: str, name: str) -> User:
        """新增用户：重复邮箱会触发 UNIQUE 约束，抛出 sqlite3.IntegrityError。"""
        with atomic(self.conn):
            cursor = self.conn.execute('INSERT INTO users (email, name) VALUES (?, ?)', (email, name))
        return User(email=email, name=name, id=cursor.lastrowid)

    def by_email(self, email: str) -> User | None:
        """按邮箱查询（参数化查询，防止 SQL 注入）。"""
        row = self.conn.execute('SELECT id, email, name FROM users WHERE email = ?', (email,)).fetchone()
        return None if row is None else User(id=row['id'], email=row['email'], name=row['name'])

    def get(self, user_id: int) -> User | None:
        """按主键查询。"""
        row = self.conn.execute('SELECT id, email, name FROM users WHERE id = ?', (user_id,)).fetchone()
        return None if row is None else User(id=row['id'], email=row['email'], name=row['name'])

    def rename(self, user_id: int, name: str) -> bool:
        """修改昵称，返回是否真的改到了一行。"""
        with atomic(self.conn):
            cursor = self.conn.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
        return cursor.rowcount == 1

    def delete(self, user_id: int) -> bool:
        """删除用户，外键的 ON DELETE CASCADE 会同时删除他的全部笔记。"""
        with atomic(self.conn):
            cursor = self.conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        return cursor.rowcount == 1


class NoteRepo:
    """笔记仓库：封装 notes 表的操作。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(self, note: Note) -> Note:
        """新增笔记：user_id 不存在时外键约束会拒绝写入。"""
        with atomic(self.conn):
            cursor = self.conn.execute(
                'INSERT INTO notes (user_id, title, body) VALUES (?, ?, ?)',
                (note.user_id, note.title, note.body),
            )
        return Note(user_id=note.user_id, title=note.title, body=note.body, id=cursor.lastrowid)

    def list_by_user(self, user_id: int) -> list[Note]:
        """列出某用户的全部笔记，按 id 升序（走 idx_notes_user 索引）。"""
        rows = self.conn.execute(
            'SELECT id, user_id, title, body FROM notes WHERE user_id = ? ORDER BY id', (user_id,)
        ).fetchall()
        return [Note(id=r['id'], user_id=r['user_id'], title=r['title'], body=r['body']) for r in rows]

    def search(self, keyword: str) -> list[Note]:
        """按标题关键词模糊搜索。先转义 LIKE 的通配符 % 与 _，再用参数传入。"""
        escaped = keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        rows = self.conn.execute(
            "SELECT id, user_id, title, body FROM notes WHERE title LIKE ? ESCAPE '\\' ORDER BY id",
            (f'%{escaped}%',),
        ).fetchall()
        return [Note(id=r['id'], user_id=r['user_id'], title=r['title'], body=r['body']) for r in rows]


def find_user_unsafe(conn: sqlite3.Connection, email: str) -> list[sqlite3.Row]:
    """直观版（反面教材）：f-string 拼接 SQL，输入 `' OR '1'='1` 会返回所有用户。"""
    return conn.execute(f"SELECT id, email, name FROM users WHERE email = '{email}'").fetchall()


def register_with_welcome(conn: sqlite3.Connection, email: str, name: str) -> User:
    """事务示例：同时写用户与欢迎笔记。任何一步失败，两步都会回滚。"""
    users = UserRepo(conn)
    notes = NoteRepo(conn)
    with atomic(conn):  # 外层事务：内部 users.create / notes.add 用的是保存点，不会提前提交
        user = users.create(email, name)
        assert user.id is not None
        notes.add(Note(user_id=user.id, title='欢迎', body=f'你好，{name}'))
    return user


def run_tests() -> None:
    """自动化断言测试：覆盖迁移幂等、CRUD、外键级联、事务回滚、注入防护与关键词转义。"""
    conn = connect()
    assert migrate(conn) == 3
    assert migrate(conn) == 3  # 重复迁移不会报错，版本保持不变

    users = UserRepo(conn)
    notes = NoteRepo(conn)

    # 1. 新增与查询
    alice = users.create('alice@example.com', 'Alice')
    assert alice.id is not None
    assert users.by_email('alice@example.com') == alice
    assert users.get(alice.id) == alice
    assert users.by_email('nobody@example.com') is None

    # 2. 唯一约束：同一邮箱不能注册两次
    try:
        users.create('alice@example.com', 'Alice2')
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError('重复邮箱必须被 UNIQUE 约束拒绝')

    # 3. 更新
    assert users.rename(alice.id, 'Alice 2') is True
    assert users.get(alice.id).name == 'Alice 2'  # type: ignore[union-attr]
    assert users.rename(9999, 'ghost') is False

    # 4. 外键：笔记必须属于存在的用户
    try:
        notes.add(Note(user_id=9999, title='孤儿笔记'))
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError('外键必须阻止写入不存在用户的笔记')

    # 5. 笔记增查与关键词搜索（含通配符字符，应按字面匹配）
    notes.add(Note(user_id=alice.id, title='100% 完成', body='第一条'))
    notes.add(Note(user_id=alice.id, title='a_b 测试', body='第二条'))
    notes.add(Note(user_id=alice.id, title='其它内容', body='第三条'))
    assert [n.title for n in notes.list_by_user(alice.id)] == ['100% 完成', 'a_b 测试', '其它内容']
    assert [n.title for n in notes.search('%')] == ['100% 完成']  # % 只按字面匹配，不当作通配符
    assert [n.title for n in notes.search('_')] == ['a_b 测试']
    assert notes.search('不存在') == []

    # 6. 事务回滚：外层事务里任一步失败，已写入的用户也必须撤销
    try:
        with atomic(conn):
            users.create('bob@example.com', 'Bob')
            raise RuntimeError('模拟中途失败')
    except RuntimeError:
        pass
    assert users.by_email('bob@example.com') is None

    # 7. 事务成功：欢迎笔记与用户一起写入
    carol = register_with_welcome(conn, 'carol@example.com', 'Carol')
    assert [n.title for n in notes.list_by_user(carol.id)] == ['欢迎']  # type: ignore[arg-type]

    # 8. 级联删除：删除用户时，他的笔记一起消失
    assert users.delete(alice.id) is True
    assert notes.list_by_user(alice.id) == []
    assert notes.search('第一条') == []

    # 9. 注入对照：拼接 SQL 会泄露全部用户，参数化查询则查不到
    injected = "' OR '1'='1"
    assert len(find_user_unsafe(conn, injected)) >= 1
    assert users.by_email(injected) is None

    print('✅ 数据层迁移、事务与参数化查询所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 数据层：迁移与事务 {'*' * 12}", sep='', end='\n\n')
    conn = connect()
    print('迁移到版本:', migrate(conn))
    user = register_with_welcome(conn, 'demo@example.com', 'Demo')
    for note in NoteRepo(conn).list_by_user(user.id):  # type: ignore[arg-type]
        print(f'笔记 #{note.id}: {note.title} - {note.body}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
