# `08_ai_fullstack_fastapi` | AI 全栈：FastAPI 后端与认证

- **来源**: [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)（推荐度排名 2，MIT 许可）
- **学习目标**: 先用标准库吃透「路由 + 参数校验 + 认证」的原理，再去读官方模板的 `backend/` 与 `frontend/`，最后把 RAG / Agent 包装成带登录和数据库的产品。
- **前置语法**: `dict`、`re`、`dataclass`、装饰器基础
- **环境**: 本目录脚本只用标准库，不需要安装 FastAPI。真正跑官方模板需要 Docker、PostgreSQL、Node.js，先看它的 `development.md`。

## 章节映射与进度

| 编号 | 官方模板对应部分 | 本地文件 | 核心点 | 状态 |
| --- | --- | --- | --- | --- |
| `00_` | FastAPI 路由与 Pydantic 校验 | [00_http_basics/00_router_and_validation.py](./00_http_basics/00_router_and_validation.py) | 路径参数、请求体校验、404 / 405 / 422 | ✅ 已完成 |
| `01_` | 后端安全模块（JWT、密码哈希） | [01_auth/00_jwt_and_password.py](./01_auth/00_jwt_and_password.py) | HS256 签名、过期、防篡改、加盐哈希 | ✅ 已完成 |
| `02_` | SQLModel + PostgreSQL | [02_database/00_sqlite_repository.py](./02_database/00_sqlite_repository.py) | 版本化迁移、外键级联、可嵌套事务（SAVEPOINT）、参数化查询防注入（sqlite3 版，思想对应 SQLModel） | ✅ 已完成 |
| `03_` | Docker Compose 与部署 | [03_deploy/00_config_health_dockerfile.py](./03_deploy/00_config_health_dockerfile.py) | 12-Factor 配置校验、健康检查聚合 (200/503)、Dockerfile 生成与静态检查 | ✅ 已完成 |
| `04_` | Pytest 与 CI | [04_testing_ci/00_mini_pytest_and_ci.py](./04_testing_ci/00_mini_pytest_and_ci.py) | 迷你 pytest（fixture / 参数化 / 失败隔离）、Fake 替身、GitHub Actions 工作流检查 | ✅ 已完成 |

**本目录总题数：5（已完成 5，待生成 0）**

## 验证

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 08_ai_fullstack_fastapi
```
