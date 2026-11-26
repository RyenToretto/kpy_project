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
| `02_` | SQLModel + PostgreSQL | 可用 `py-study-generator` 按需生成 | ORM 与迁移（可先学 `01_python_100_days` 的 SQLite） | 📝 待生成 |
| `03_` | Docker Compose 与部署 | 可用 `py-study-generator` 按需生成 | 容器编排、反向代理、HTTPS | 📝 待生成 |
| `04_` | Pytest 与 CI | 可用 `py-study-generator` 按需生成 | 接口测试、GitHub Actions | 📝 待生成 |

**本目录总题数：5**（已完成 2，待生成 3）

## 验证

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 08_ai_fullstack_fastapi
```
