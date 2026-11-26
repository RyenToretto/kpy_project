"""
[主题]: JSON-RPC 2.0 消息格式 (request / response / error / notification)
[来源]: microsoft/mcp-for-beginners 第 1 章「MCP 基础概念」(本文件为自行重写的学习版，不依赖官方 SDK)
[难度]: Easy
[前置知识]: 00_basic 语法主线、字典、json 模块、函数

一、主题说明
MCP（Model Context Protocol）让大模型应用用统一方式调用外部工具与数据。它的底层是 JSON-RPC 2.0：
- request: 带 id 的请求，必须收到 response；
- response: 与请求 id 对应，包含 result 或 error 二者之一；
- notification: 不带 id 的单向通知，不需要回复。
理解这四种消息，就理解了 MCP 通信的全部骨架。

二、解法对比（以「把一次调用编码成 JSON 再解析」为例）
1. 直观版 make_request_text: 手写字符串拼接 JSON。
   - 容易漏引号、逗号，遇到中文或特殊字符很容易出错。
2. 进阶版 make_request / parse_message: 用字典组装再 json.dumps，解析时统一校验版本号与字段。
   - 时间复杂度 O(消息长度)，空间复杂度 O(消息长度)

三、真实用途
- 大数据: 分布式系统里的 RPC 调用（如 gRPC、Dubbo）同样需要请求 id 来匹配响应。
- 数据分析: 让大模型通过 MCP 调用数据库或指标服务时，底层都是这种消息结构。
- AI Agent / RAG: Agent 调用工具的每一步都是一次 request/response，日志里按 id 追踪最清楚。
- 全栈开发: 前后端的 JSON API 与 JSON-RPC 的区别只在约定，理解它有助于设计接口。
"""

from __future__ import annotations

import json
from typing import Any

JSONRPC_VERSION = '2.0'

# JSON-RPC 2.0 规定的标准错误码
ERROR_PARSE = -32700  # 不是合法 JSON
ERROR_INVALID_REQUEST = -32600  # 缺少必要字段
ERROR_METHOD_NOT_FOUND = -32601  # 方法不存在
ERROR_INVALID_PARAMS = -32602  # 参数不合法


def make_request(request_id: int, method: str, params: dict[str, Any] | None = None) -> str:
    """组装请求并序列化为 JSON 字符串；params 没有时省略该字段。"""
    message: dict[str, Any] = {'jsonrpc': JSONRPC_VERSION, 'id': request_id, 'method': method}
    if params is not None:
        message['params'] = params
    return json.dumps(message, ensure_ascii=False)


def make_notification(method: str, params: dict[str, Any] | None = None) -> str:
    """通知没有 id，接收方不需要回复。"""
    message: dict[str, Any] = {'jsonrpc': JSONRPC_VERSION, 'method': method}
    if params is not None:
        message['params'] = params
    return json.dumps(message, ensure_ascii=False)


def make_result(request_id: int, result: Any) -> str:
    """成功响应：result 与请求 id 一一对应。"""
    return json.dumps({'jsonrpc': JSONRPC_VERSION, 'id': request_id, 'result': result}, ensure_ascii=False)


def make_error(request_id: int | None, code: int, message: str) -> str:
    """失败响应：error 字段包含错误码与说明。无法解析出 id 时 id 为 null。"""
    error = {'code': code, 'message': message}
    return json.dumps({'jsonrpc': JSONRPC_VERSION, 'id': request_id, 'error': error}, ensure_ascii=False)


def parse_message(text: str) -> dict[str, Any]:
    """解析并校验一条消息，返回字典；格式错误时抛出 ValueError，并附上标准错误码。"""
    try:
        message = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f'{ERROR_PARSE}: 不是合法 JSON') from exc
    if not isinstance(message, dict) or message.get('jsonrpc') != JSONRPC_VERSION:
        raise ValueError(f'{ERROR_INVALID_REQUEST}: 缺少 jsonrpc 2.0 版本号')
    return message


def classify(message: dict[str, Any]) -> str:
    """判断消息类型：有 method 且有 id 是 request；有 method 无 id 是 notification；有 result 或 error 是 response。"""
    if 'method' in message and 'id' in message:
        return 'request'
    if 'method' in message:
        return 'notification'
    if 'result' in message or 'error' in message:
        return 'response'
    return 'invalid'


def make_request_text_naive(request_id: int, method: str) -> str:
    """直观版：手写字符串拼接，没有参数时的格式必须手动处理（反面教材，容易写出非法 JSON）。"""
    return '{"jsonrpc": "2.0", "id": ' + str(request_id) + ', "method": "' + method + '"}'


def run_tests() -> None:
    """自动化断言测试：覆盖四种消息、错误码与非法输入。"""
    # 1. 请求：包含 jsonrpc / id / method / params
    req = parse_message(make_request(1, 'tools/list'))
    assert req == {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list'}
    assert classify(req) == 'request'

    # 2. 带参数的请求
    req_with_params = parse_message(make_request(2, 'tools/call', {'name': 'add', 'arguments': {'a': 1, 'b': 2}}))
    assert req_with_params['params']['arguments'] == {'a': 1, 'b': 2}

    # 3. 通知没有 id
    note = parse_message(make_notification('notifications/initialized'))
    assert classify(note) == 'notification' and 'id' not in note

    # 4. 响应：result 与 error 两种形式
    ok = parse_message(make_result(1, {'tools': []}))
    assert classify(ok) == 'response' and ok['result'] == {'tools': []}
    failed = parse_message(make_error(1, ERROR_METHOD_NOT_FOUND, '方法不存在'))
    assert failed['error']['code'] == -32601

    # 5. 中文参数能正确往返（ensure_ascii=False 时不会被转义）
    assert '你好' in make_request(3, 'echo', {'text': '你好'})

    # 6. 非法输入：非 JSON、缺少版本号都要报错，并带上标准错误码
    try:
        parse_message('{不是 json')
    except ValueError as exc:
        assert str(ERROR_PARSE) in str(exc)
    else:
        raise AssertionError('非法 JSON 必须报错')

    try:
        parse_message('{"id": 1, "method": "x"}')
    except ValueError as exc:
        assert str(ERROR_INVALID_REQUEST) in str(exc)
    else:
        raise AssertionError('缺少 jsonrpc 版本号必须报错')

    # 7. 直观版在无参数时结果与标准写法的字段一致
    assert json.loads(make_request_text_naive(5, 'ping')) == json.loads(make_request(5, 'ping'))

    print('✅ JSON-RPC 消息格式所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} JSON-RPC 消息格式 {'*' * 12}", sep='', end='\n\n')
    samples = {
        '请求 request': make_request(1, 'tools/call', {'name': 'add', 'arguments': {'a': 2, 'b': 3}}),
        '通知 notification': make_notification('notifications/initialized'),
        '成功 response': make_result(1, {'content': [{'type': 'text', 'text': '5'}]}),
        '失败 error': make_error(1, ERROR_METHOD_NOT_FOUND, '方法不存在'),
    }
    for title, text in samples.items():
        print(f'{title}: {text}')
        print(f'  -> 类型: {classify(parse_message(text))}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
