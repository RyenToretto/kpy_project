"""
[主题]: 测试与持续集成：迷你 pytest（fixture / 参数化 / 失败隔离）、测试替身 (Fake)、GitHub Actions 工作流检查
[来源]: fastapi/full-stack-fastapi-template 的 pytest 测试与 GitHub Actions CI 思路（本文件为自行重写的标准库学习版）
[难度]: Medium
[前置知识]: 02_database (数据层)、03_deploy (配置与 Dockerfile)、函数签名 inspect、装饰器、importlib

一、主题说明
没有测试的后端，每次改动都是赌博。这一章要理解三件事：
1. 测试结构: test_ 函数 + fixture（每个测试独立的依赖准备）+ parametrize（同一断言跑多组数据）；
2. 测试替身 (test double): 用 FakeMailer 代替真实邮件服务，测试不联网、不花钱、结果可重复；
3. CI: 每次 push / PR 自动跑测试，失败就拦住合并。工作流文件本身也可以用代码生成和检查，防止把密钥写进去。
真实项目用 pytest 即可；这里实现一个迷你版，让你看清 pytest 背后做了什么，但不依赖第三方库。

二、解法对比（以「注册用户并发欢迎邮件，邮件失败则用户不能残留」为例）
1. 直观版 register_naive: 先写库，再发邮件，邮件失败时用户已经存在，产生“有账号却没收到邮件”的脏数据。
   - 时间复杂度 O(1)，但没有一致性保证。
2. 进阶版 register_and_welcome: 写库与发信放在同一个事务里，发信失败整体回滚。
   - 测试里用 FakeMailer 制造失败，验证回滚；fixture 保证每个测试都有全新的内存数据库，互不干扰。

三、真实用途
- 大数据: 数据管道的单元测试（用假数据源替代真实数据湖）决定了上线前能否发现 schema 变化。
- 数据分析: 指标口径的回归测试，防止改一行 SQL 把报表数字悄悄改掉。
- AI Agent / RAG: 用 Fake LLM 与 Fake 向量库做测试，CI 不需要 API Key 也能验证检索与编排逻辑。
- 全栈开发: 每次合并自动跑测试与 Dockerfile 检查，是副业交付时证明“代码可用”的最低标准。
"""

from __future__ import annotations

import importlib.util
import inspect
import re
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any


def load_module(name: str, path: Path) -> ModuleType:
    """按文件路径加载模块：目录名以数字开头无法直接 import，需要 spec_from_file_location。
    注意：dataclass 等机制要求模块已登记在 sys.modules 中，所以加载前要先注册。"""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'无法加载 {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[1]
REPO = load_module('sqlite_repository_under_test', ROOT / '02_database' / '00_sqlite_repository.py')


# ---------- 迷你 pytest：装饰器与运行器 ----------

def fixture(fn: Callable[..., Any]) -> Callable[..., Any]:
    """标记 fixture：测试函数的同名参数会自动注入 fixture 的返回值，且每个测试都重新创建一次。"""
    fn._is_fixture = True  # type: ignore[attr-defined]
    return fn


def parametrize(argnames: str, cases: list[tuple[Any, ...]]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """参数化：同一个测试函数用多组数据各跑一遍，argnames 形如 'email,expected'。"""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn._params = (argnames, cases)  # type: ignore[attr-defined]
        return fn
    return decorator


def collect(namespace: dict[str, Any]) -> list[tuple[str, Callable[..., Any], dict[str, Any]]]:
    """收集 test_ 开头的函数，参数化的会展开成多个用例（按定义顺序）。"""
    cases: list[tuple[str, Callable[..., Any], dict[str, Any]]] = []
    for name, obj in namespace.items():
        if not (name.startswith('test_') and callable(obj)):
            continue
        params = getattr(obj, '_params', None)
        if params is None:
            cases.append((name, obj, {}))
            continue
        argnames, values = params
        keys = [item.strip() for item in argnames.split(',')]
        for index, row in enumerate(values):
            cases.append((f'{name}[{index}]', obj, dict(zip(keys, row))))
    return cases


def run_case(fn: Callable[..., Any], kwargs: dict[str, Any], fixtures: dict[str, Callable[..., Any]]) -> str | None:
    """运行单个用例：返回 None 表示通过，返回字符串表示失败原因。异常只影响本用例，不会中断整个套件。"""
    args: dict[str, Any] = {}
    for param in inspect.signature(fn).parameters:
        if param in kwargs:
            args[param] = kwargs[param]
        elif param in fixtures:
            args[param] = fixtures[param]()  # 每次都调用一次 fixture，保证用例之间互不污染
        else:
            return f'找不到 fixture: {param}'
    try:
        fn(**args)
    except AssertionError as exc:
        return f'断言失败: {exc}'
    except Exception as exc:  # 测试代码自身的异常也记为失败
        return f'{type(exc).__name__}: {exc}'
    return None


def run_suite(namespace: dict[str, Any]) -> tuple[int, list[str]]:
    """运行命名空间中的全部测试，返回 (通过数, 失败信息列表)。"""
    fixtures = {name: obj for name, obj in namespace.items() if getattr(obj, '_is_fixture', False)}
    passed = 0
    failures: list[str] = []
    for case_name, fn, kwargs in collect(namespace):
        error = run_case(fn, kwargs, fixtures)
        if error is None:
            passed += 1
        else:
            failures.append(f'{case_name}: {error}')
    return passed, failures


# ---------- 被测业务：注册 + 欢迎邮件（依赖注入一个邮件接口） ----------

EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class FakeMailer:
    """测试替身：记录发送内容，并可设置为失败，用来模拟邮件服务宕机。"""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, subject: str) -> None:
        if self.fail:
            raise ConnectionError('邮件服务不可用')
        self.sent.append((to, subject))


def register_naive(conn: Any, mailer: Any, email: str, name: str) -> Any:
    """直观版（反面教材）：先写库再发邮件，邮件失败时用户已经存在，留下脏数据。"""
    user = REPO.UserRepo(conn).create(email, name)
    mailer.send(email, '欢迎')
    return user


def register_and_welcome(conn: Any, mailer: Any, email: str, name: str) -> Any:
    """进阶版：写库与发信在同一个事务中，发信失败则用户也不会保存。"""
    if not EMAIL_PATTERN.match(email):
        raise ValueError(f'邮箱格式错误: {email}')
    with REPO.atomic(conn):
        user = REPO.UserRepo(conn).create(email, name)
        mailer.send(email, '欢迎')
    return user


# ---------- CI：GitHub Actions 工作流的生成与检查 ----------

def render_workflow(python_version: str = '3.12') -> str:
    """生成测试工作流：每次 push 与 PR 都在干净的 Ubuntu 上安装依赖并运行 pytest。"""
    return '\n'.join([
        'name: tests',
        'on:',
        '  push:',
        '  pull_request:',
        'permissions:',
        '  contents: read',
        'jobs:',
        '  test:',
        '    runs-on: ubuntu-latest',
        '    steps:',
        '      - uses: actions/checkout@v4',
        '      - uses: actions/setup-python@v5',
        '        with:',
        f'          python-version: "{python_version}"',
        '      - run: python -m pip install -r requirements.txt pytest',
        '      - run: python -m pytest -q',
    ]) + '\n'


def check_workflow(text: str) -> list[str]:
    """检查工作流：必须有触发器、测试步骤、最小权限；禁止 pull_request_target、未固定版本的 Action 与打印密钥。"""
    issues: list[str] = []
    for required in ['on:', 'jobs:', 'pytest', 'python-version', 'permissions:']:
        if required not in text:
            issues.append(f'缺少 {required}')
    if 'pull_request_target' in text:
        issues.append('禁止使用 pull_request_target：会在不可信的 PR 代码上拿到密钥')
    for match in re.finditer(r'uses:\s*(\S+)', text):
        ref = match.group(1)
        if '@' not in ref or ref.split('@', 1)[1] in {'main', 'master', 'latest'}:
            issues.append(f'Action 必须固定版本号: {ref}')
    if re.search(r'echo\s+.*\$\{\{\s*secrets\.', text):
        issues.append('禁止在日志中打印 secrets')
    return issues


# ---------- 测试用例 ----------

@fixture
def conn() -> Any:
    """每个测试一个全新的内存数据库，并完成迁移。"""
    connection = REPO.connect()
    REPO.migrate(connection)
    return connection


@fixture
def mailer() -> FakeMailer:
    """每个测试一个全新的假邮件发送器。"""
    return FakeMailer()


@parametrize('email,ok', [('alice@example.com', True), ('bad-address', False), ('a@b', False), ('', False)])
def test_email_format(email: str, ok: bool) -> None:
    """参数化：同一断言跑多组邮箱，覆盖合法与非法格式。"""
    assert bool(EMAIL_PATTERN.match(email)) is ok


def test_register_persists_and_mails(conn: Any, mailer: FakeMailer) -> None:
    """正常注册：用户入库，并且发出一封欢迎邮件。"""
    user = register_and_welcome(conn, mailer, 'alice@example.com', 'Alice')
    assert user.id is not None
    assert REPO.UserRepo(conn).by_email('alice@example.com') is not None
    assert mailer.sent == [('alice@example.com', '欢迎')]


def test_register_rolls_back_when_mail_fails(conn: Any) -> None:
    """邮件失败时，事务回滚：不能留下“有账号、没邮件”的用户。"""
    broken_mailer = FakeMailer(fail=True)
    try:
        register_and_welcome(conn, broken_mailer, 'bob@example.com', 'Bob')
    except ConnectionError:
        pass
    else:
        raise AssertionError('邮件失败必须向上抛出')
    assert REPO.UserRepo(conn).by_email('bob@example.com') is None


def test_naive_register_leaves_dirty_data(conn: Any) -> None:
    """对照实验：直观版在邮件失败时会留下脏数据，说明事务的必要性。"""
    try:
        register_naive(conn, FakeMailer(fail=True), 'carol@example.com', 'Carol')
    except ConnectionError:
        pass
    assert REPO.UserRepo(conn).by_email('carol@example.com') is not None


def test_invalid_email_rejected_before_db(conn: Any, mailer: FakeMailer) -> None:
    """非法邮箱在访问数据库之前就被拒绝，不会产生任何写入。"""
    try:
        register_and_welcome(conn, mailer, 'not-an-email', 'X')
    except ValueError:
        pass
    else:
        raise AssertionError('非法邮箱必须报错')
    assert mailer.sent == []
    assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0


def test_fixtures_are_isolated(conn: Any) -> None:
    """隔离性：上一条用例写入的数据，在本用例中必须不存在。"""
    assert conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0


def run_tests() -> None:
    """自动化断言测试：先验证迷你 pytest 自身（失败能被捕获、参数化能展开），再跑业务与 CI 检查。"""
    # 0. 元测试：迷你 pytest 必须能发现失败，而不是把失败当成功
    def always_fail() -> None:
        assert 1 == 2, '故意失败'

    error = run_case(always_fail, {}, {})
    assert error is not None and '故意失败' in error

    # 0.1 参数化展开：2 组数据应生成 2 个用例
    def param_demo(x: int) -> None:
        assert x > 0

    demo = parametrize('x', [(1,), (2,)])(param_demo)
    names = [name for name, _, _ in collect({'test_demo': demo})]
    assert names == ['test_demo[0]', 'test_demo[1]']

    # 1. 运行本文件中的全部测试，必须全部通过
    passed, failures = run_suite(globals())
    assert failures == [], f'存在失败用例: {failures}'
    assert passed == 9  # 参数化 4 组 + 其余 5 个测试

    # 2. CI 工作流：生成的文件必须通过自己的检查
    workflow = render_workflow()
    assert check_workflow(workflow) == []
    assert 'python-version: "3.12"' in workflow and 'pytest' in workflow

    # 3. 反面工作流：各类风险都要被查出来
    bad = '\n'.join([
        'on:',
        '  pull_request_target:',
        'jobs:',
        '  test:',
        '    steps:',
        '      - uses: actions/checkout@main',
        '      - run: echo ${{ secrets.API_KEY }}',
    ])
    joined = '\n'.join(check_workflow(bad))
    for keyword in ['pull_request_target', '固定版本', '打印 secrets', 'permissions', 'pytest']:
        assert keyword in joined, f'应检出问题: {keyword}'

    print(f'✅ 迷你 pytest 与 CI 检查通过！业务用例 {passed} 个全部通过。')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 测试与持续集成 {'*' * 12}", sep='', end='\n\n')
    passed, failures = run_suite(globals())
    print(f'迷你 pytest 结果: 通过 {passed}，失败 {len(failures)}')
    for item in failures:
        print('  -', item)
    print(render_workflow())
    run_tests()


if __name__ == '__main__':
    bootstrap()
