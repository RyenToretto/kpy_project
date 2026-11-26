"""
[主题]: 迷你 Web 路由器 + 请求参数校验（理解 FastAPI 在做什么）
[来源]: fastapi/full-stack-fastapi-template 的后端路由与 Pydantic 校验思想
[难度]: Medium
[前置知识]: dict、re 正则、dataclass、装饰器

一、主题说明
FastAPI 的核心可以拆成两件事：
1) 路由: 把 (HTTP 方法, 路径) 映射到处理函数，并从路径里取出参数；
2) 校验: 请求体或参数不合法时返回 422，而不是让程序崩溃。
这里用标准库实现一个迷你版，帮你看清装饰器注册路由的原理。

二、解法对比
1. 直观版 handle_basic:
   - 用 dict 精确匹配 (方法, 路径)，不支持路径参数。
   - 查找 O(1)，但 /items/1、/items/2 要各写一条。
2. 进阶版 MiniApp:
   - 装饰器注册路由，把 {item_id} 转成正则的命名分组；
   - 区分 404（路径不存在）与 405（路径存在但方法不对）；
   - 校验失败统一返回 422 与错误列表。
   - 查找 O(路由数)，路由很多时可换成前缀树。

三、真实用途
- 全栈开发: 看懂 `@app.get('/items/{item_id}')` 背后的原理，排查 404 / 405 / 422 更快。
- AI Agent / RAG: 对外暴露 /chat、/ingest 接口时，参数校验是防脏数据和提示注入的第一道门。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

Response = tuple[int, dict[str, Any]]


class ValidationError(Exception):
    """参数校验失败，携带错误列表，对应 HTTP 422。"""

    def __init__(self, errors: list[str]) -> None:
        super().__init__('; '.join(errors))
        self.errors = errors


@dataclass
class ItemIn:
    """请求体模型，类似 Pydantic 的 BaseModel。"""

    name: str
    price: float


def parse_item(body: dict[str, Any] | None) -> ItemIn:
    """校验并构造 ItemIn，所有问题一次性返回。"""
    errors: list[str] = []
    data = body or {}
    name = data.get('name')
    price = data.get('price')
    if not isinstance(name, str) or not name.strip():
        errors.append('name 必须是非空字符串')
    if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
        errors.append('price 必须是不小于 0 的数字')
    if errors:
        raise ValidationError(errors)
    return ItemIn(name=name.strip(), price=float(price))


def to_int(field_name: str, raw: str) -> int:
    """把路径参数转成整数，失败就报 422。"""
    if not raw.isdigit():
        raise ValidationError([f'{field_name} 必须是整数'])
    return int(raw)


def handle_basic(method: str, path: str) -> Response:
    """直观版：精确匹配，不支持路径参数。"""
    routes = {('GET', '/health'): (200, {'status': 'ok'})}
    return routes.get((method.upper(), path), (404, {'detail': 'Not Found'}))


class MiniApp:
    """进阶版：装饰器注册路由 + 路径参数 + 统一错误码。"""

    def __init__(self) -> None:
        self._routes: list[tuple[str, re.Pattern[str], Callable[..., Response]]] = []

    def route(self, method: str, path: str) -> Callable[[Callable[..., Response]], Callable[..., Response]]:
        # 把 /items/{item_id} 转成 ^/items/(?P<item_id>[^/]+)$
        pattern = re.compile('^' + re.sub(r'\{(\w+)\}', r'(?P<\1>[^/]+)', path) + '$')

        def decorator(func: Callable[..., Response]) -> Callable[..., Response]:
            self._routes.append((method.upper(), pattern, func))
            return func

        return decorator

    def handle(self, method: str, path: str, body: dict[str, Any] | None = None) -> Response:
        path_matched = False
        for route_method, pattern, func in self._routes:
            match = pattern.match(path)
            if match is None:
                continue
            path_matched = True
            if route_method != method.upper():
                continue
            try:
                return func(body=body, **match.groupdict())
            except ValidationError as exc:
                return 422, {'detail': exc.errors}
        if path_matched:
            return 405, {'detail': 'Method Not Allowed'}
        return 404, {'detail': 'Not Found'}


def build_app() -> MiniApp:
    app = MiniApp()

    @app.route('GET', '/health')
    def health(body: dict[str, Any] | None) -> Response:
        return 200, {'status': 'ok'}

    @app.route('GET', '/items/{item_id}')
    def read_item(body: dict[str, Any] | None, item_id: str) -> Response:
        return 200, {'item_id': to_int('item_id', item_id)}

    @app.route('POST', '/items')
    def create_item(body: dict[str, Any] | None) -> Response:
        item = parse_item(body)
        return 201, {'name': item.name, 'price': item.price}

    return app


def run_tests() -> None:
    """自动化断言测试。"""
    assert handle_basic('GET', '/health') == (200, {'status': 'ok'})
    assert handle_basic('GET', '/items/1')[0] == 404  # 直观版不支持路径参数

    app = build_app()
    assert app.handle('GET', '/health') == (200, {'status': 'ok'})
    assert app.handle('GET', '/items/3') == (200, {'item_id': 3})
    assert app.handle('GET', '/items/abc')[0] == 422
    assert app.handle('POST', '/items', {'name': ' 书 ', 'price': 9.9}) == (201, {'name': '书', 'price': 9.9})

    status, payload = app.handle('POST', '/items', {'name': '', 'price': -1})
    assert status == 422 and len(payload['detail']) == 2  # 两个错误一次性返回
    assert app.handle('POST', '/items', {'name': 'x', 'price': True})[0] == 422  # bool 不算数字

    assert app.handle('GET', '/nope')[0] == 404
    assert app.handle('DELETE', '/health')[0] == 405
    print('✅ 迷你路由器所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 迷你 Web 路由器与校验 {'*' * 12}", sep='', end='\n\n')
    app = build_app()
    for method, path, body in [
        ('GET', '/health', None),
        ('GET', '/items/42', None),
        ('GET', '/items/abc', None),
        ('POST', '/items', {'name': '笔记本', 'price': 5}),
        ('POST', '/items', {'name': '', 'price': -1}),
    ]:
        print(f'{method:<5}{path:<12} -> {app.handle(method, path, body)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
