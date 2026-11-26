"""
[主题]: 部署三件套的可测部分：环境变量配置校验 (12-Factor)、健康检查聚合、Dockerfile 静态检查
[来源]: fastapi/full-stack-fastapi-template 的 Docker Compose 部署与健康检查思路（本文件为自行重写的标准库学习版）
[难度]: Medium
[前置知识]: 02_database (数据库连接串)、dict/Mapping、字符串处理、Callable、异常

一、主题说明
把应用放到服务器上，最容易出事的不是代码，而是配置和部署细节：
1. 配置: 密钥、数据库地址、端口都从环境变量读取（12-Factor），生产环境必须校验，不能静默使用默认密钥；
2. 健康检查: 负载均衡与 Docker 通过 /health 判断实例是否可用，应检查依赖（数据库）是否正常；
3. 镜像: Dockerfile 要用固定版本基础镜像、多阶段构建、非 root 运行、配置 HEALTHCHECK，并且利用缓存加快构建。
这三点都可以用纯 Python 做“离线检查”，不需要真的启动容器，适合放进 CI。

二、解法对比（以「生产环境配置」为例）
1. 直观版 load_settings_naive: 用 os.environ.get('SECRET_KEY', 'changeme')，忘设变量就用弱密钥上线。
   - 时间复杂度 O(1)，最省事，也最危险。
2. 进阶版 load_settings: 收集全部错误一次性报告，生产环境强制检查密钥强度与端口范围。
   - 时间复杂度 O(配置项数)，启动即失败（fail fast），比上线后被攻破更好。

三、真实用途
- 大数据: 数据任务的连接串、访问密钥走环境变量，避免泄露到代码仓库。
- 数据分析: 健康检查确保调度器只把请求派给数据库可用的报表服务。
- AI Agent / RAG: 模型 API Key、向量库地址都是环境变量，Dockerfile 静态检查能挡住把密钥写进镜像的低级错误。
- 全栈开发: 副业交付项目时，一套 Dockerfile + 配置校验 + 健康检查，就是客户能直接部署的最小交付物。
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass

WEAK_SECRETS = {'changeme', 'secret', 'password', ''}


@dataclass(frozen=True)
class Settings:
    """应用配置：全部来自环境变量，创建后不可修改。"""

    app_env: str
    secret_key: str
    database_url: str
    port: int


def load_settings_naive(env: Mapping[str, str]) -> Settings:
    """直观版（反面教材）：缺失就用默认值，生产环境也可能带着 changeme 上线。"""
    return Settings(
        app_env=env.get('APP_ENV', 'dev'),
        secret_key=env.get('SECRET_KEY', 'changeme'),
        database_url=env.get('DATABASE_URL', 'sqlite:///./app.db'),
        port=int(env.get('PORT', '8000')),
    )


def load_settings(env: Mapping[str, str]) -> Settings:
    """进阶版：收集全部配置错误后一次性报错；生产环境强制要求强密钥与合法端口。"""
    errors: list[str] = []
    app_env = env.get('APP_ENV', 'dev')
    if app_env not in {'dev', 'prod'}:
        errors.append(f'APP_ENV 只能是 dev 或 prod，当前为 {app_env!r}')

    secret_key = env.get('SECRET_KEY', '')
    if app_env == 'prod':
        if secret_key.lower() in WEAK_SECRETS or len(secret_key) < 32:
            errors.append('生产环境 SECRET_KEY 必须是至少 32 位的非默认值')
    elif not secret_key:
        secret_key = 'dev-only-key'  # 只有开发环境允许使用固定的临时密钥

    database_url = env.get('DATABASE_URL', 'sqlite:///./app.db')
    if not database_url.startswith(('sqlite:///', 'postgresql://')):
        errors.append(f'DATABASE_URL 协议不支持: {database_url.split(":", 1)[0]!r}')

    raw_port = env.get('PORT', '8000')
    port = int(raw_port) if raw_port.isdigit() else -1
    if not 1 <= port <= 65535:
        errors.append(f'PORT 必须是 1~65535 之间的整数，当前为 {raw_port!r}')

    if errors:
        raise ValueError('配置错误: ' + '; '.join(errors))
    return Settings(app_env=app_env, secret_key=secret_key, database_url=database_url, port=port)


CheckFn = Callable[[], bool]


def health_report(checks: Mapping[str, CheckFn]) -> tuple[int, dict[str, str]]:
    """运行全部依赖检查：全部通过返回 200，任一失败或抛异常返回 503，供负载均衡判断实例是否可用。"""
    status: dict[str, str] = {}
    for name, check in checks.items():
        try:
            status[name] = 'ok' if check() else 'fail'
        except Exception as exc:  # 检查本身出错也算失败，不能让健康接口崩溃
            status[name] = f'error: {type(exc).__name__}'
    code = 200 if all(value == 'ok' for value in status.values()) else 503
    return code, status


def render_dockerfile(python_version: str = '3.12', port: int = 8000) -> str:
    """生成一个符合规范的多阶段 Dockerfile：固定版本、依赖先装（利用缓存）、非 root、带 HEALTHCHECK。"""
    return '\n'.join([
        f'FROM python:{python_version}-slim AS builder',
        'WORKDIR /build',
        'COPY requirements.txt .',  # 依赖清单单独复制：代码变了不必重装依赖，缓存更有效
        'RUN pip install --no-cache-dir --prefix=/install -r requirements.txt',
        '',
        f'FROM python:{python_version}-slim',
        'RUN useradd --create-home appuser',
        'WORKDIR /app',
        'COPY --from=builder /install /usr/local',
        'COPY . .',
        'USER appuser',  # 不以 root 运行，被攻破后的影响面更小
        f'EXPOSE {port}',
        f'HEALTHCHECK --interval=30s --timeout=3s CMD ["python", "-c", "import urllib.request; urllib.request.urlopen(\'http://localhost:{port}/health\')"]',
        f'CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{port}"]',
    ]) + '\n'


def lint_dockerfile(text: str) -> list[str]:
    """静态检查 Dockerfile，返回问题列表（空列表表示通过）。"""
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('#')]
    issues: list[str] = []

    from_lines = [line for line in lines if line.upper().startswith('FROM ')]
    if not from_lines:
        issues.append('缺少 FROM 指令')
    for line in from_lines:
        image = line.split()[1]
        if ':' not in image or image.endswith(':latest'):
            issues.append(f'基础镜像必须固定版本号，不能使用 latest 或不带标签: {image}')

    user_lines = [line for line in lines if line.upper().startswith('USER ')]
    if not user_lines or user_lines[-1].split()[1] in {'root', '0'}:
        issues.append('最终阶段必须切换到非 root 用户')

    if not any(line.upper().startswith('HEALTHCHECK ') for line in lines):
        issues.append('缺少 HEALTHCHECK，编排系统无法判断实例是否健康')

    if any(line.upper().startswith('ADD ') for line in lines):
        issues.append('请用 COPY 代替 ADD，ADD 会隐式解压与拉取远程地址')

    for line in lines:
        if re.match(r'(?i)ENV\s+\w*(SECRET|PASSWORD|TOKEN|API_KEY)\w*\s*=', line):
            issues.append(f'疑似把密钥写进镜像: {line}')

    copy_all = [i for i, line in enumerate(lines) if re.match(r'(?i)COPY\s+\.\s', line)]
    copy_req = [i for i, line in enumerate(lines) if 'requirements' in line and line.upper().startswith('COPY')]
    if copy_all and copy_req and copy_all[0] < copy_req[0]:
        issues.append('应先复制依赖清单并安装，再复制全部代码，否则每次改代码都会重装依赖')
    return issues


def run_tests() -> None:
    """自动化断言测试：覆盖配置校验、健康聚合、Dockerfile 生成与检查、以及反面教材对照。"""
    prod_ok = {'APP_ENV': 'prod', 'SECRET_KEY': 'x' * 40, 'DATABASE_URL': 'postgresql://db/app', 'PORT': '8080'}

    # 1. 合法的生产配置原样读取
    settings = load_settings(prod_ok)
    assert settings == Settings('prod', 'x' * 40, 'postgresql://db/app', 8080)

    # 2. 开发环境可以不设密钥，使用固定临时值
    dev = load_settings({})
    assert dev.app_env == 'dev' and dev.secret_key == 'dev-only-key' and dev.port == 8000

    # 3. 生产环境弱密钥必须被拒绝；直观版却会悄悄放行
    weak = {**prod_ok, 'SECRET_KEY': 'changeme'}
    try:
        load_settings(weak)
    except ValueError as exc:
        assert 'SECRET_KEY' in str(exc)
    else:
        raise AssertionError('生产环境弱密钥必须报错')
    assert load_settings_naive({'APP_ENV': 'prod'}).secret_key == 'changeme'  # 对照：直观版会带着弱密钥上线

    # 4. 一次性报告多个错误，而不是只报第一个
    try:
        load_settings({'APP_ENV': 'prod', 'SECRET_KEY': 'short', 'PORT': '70000', 'DATABASE_URL': 'mysql://x'})
    except ValueError as exc:
        message = str(exc)
        assert 'SECRET_KEY' in message and 'PORT' in message and 'DATABASE_URL' in message
    else:
        raise AssertionError('多个错误必须全部报告')

    # 5. 端口边界：0 与 65536 非法，65535 合法；非数字也非法
    for bad_port in ['0', '65536', 'abc']:
        try:
            load_settings({**prod_ok, 'PORT': bad_port})
        except ValueError:
            pass
        else:
            raise AssertionError(f'非法端口必须报错: {bad_port}')
    assert load_settings({**prod_ok, 'PORT': '65535'}).port == 65535

    # 6. 健康检查：全部通过 200；任一失败或抛异常 503，且异常不会冒泡
    code, status = health_report({'db': lambda: True, 'vector': lambda: True})
    assert code == 200 and status == {'db': 'ok', 'vector': 'ok'}

    def broken() -> bool:
        raise ConnectionError('连接被拒绝')

    code, status = health_report({'db': broken, 'vector': lambda: True})
    assert code == 503 and status['db'] == 'error: ConnectionError' and status['vector'] == 'ok'
    assert health_report({'db': lambda: False})[0] == 503

    # 7. 生成的 Dockerfile 必须通过自己的静态检查
    dockerfile = render_dockerfile()
    assert lint_dockerfile(dockerfile) == []
    assert 'python:3.12-slim' in dockerfile and 'USER appuser' in dockerfile and 'HEALTHCHECK' in dockerfile

    # 8. 反面教材：latest、root、ADD、密钥写进镜像、先复制代码后装依赖，都要被查出来
    bad = '\n'.join([
        'FROM python:latest',
        'ADD . /app',
        'ENV API_KEY=sk-123456',
        'COPY . .',
        'COPY requirements.txt .',
        'RUN pip install -r requirements.txt',
        'USER root',
        'CMD ["python", "app.py"]',
    ])
    issues = lint_dockerfile(bad)
    joined = '\n'.join(issues)
    for keyword in ['latest', '非 root', 'HEALTHCHECK', 'ADD', '密钥', '先复制依赖']:
        assert keyword in joined, f'应检出问题: {keyword}'

    print('✅ 配置校验、健康检查与 Dockerfile 静态检查所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 部署：配置 / 健康检查 / Dockerfile {'*' * 12}", sep='', end='\n\n')
    print(render_dockerfile())
    print('健康检查示例:', health_report({'db': lambda: True}))
    run_tests()


if __name__ == '__main__':
    bootstrap()
