"""
[主题]: 迷你 MCP 服务端 (注册工具 / initialize 握手 / tools/list / tools/call)
[来源]: microsoft/mcp-for-beginners 第 2~3 章「构建 MCP Server」(本文件为自行重写的学习版，不依赖官方 SDK)
[难度]: Medium
[前置知识]: 06_mcp_beginners/00_jsonrpc_basics (JSON-RPC 消息)、装饰器、dataclass、字典

一、主题说明
MCP 服务端要做的事情很固定：
1. initialize: 告诉客户端协议版本与自己支持的能力（这里只有 tools）；
2. tools/list: 列出所有工具的名字、说明与参数 JSON Schema，让大模型知道“能用什么”；
3. tools/call: 按名字执行工具，并把结果包装成 content 列表返回；
4. 对未知方法、未知工具、参数错误，返回标准错误码，而不是让服务端崩溃。

二、解法对比（以「如何找到并执行工具」为例）
1. 直观版 handle_if_else: 用 if/elif 判断工具名，每加一个工具都要改分发逻辑。
   - 时间复杂度 O(工具数)，扩展性差。
2. 进阶版 MiniServer.handle: 工具注册成字典 {name: Tool}，分发用一次哈希查找。
   - 时间复杂度 O(1)（查找）+ 工具函数本身的耗时，新增工具无需改分发代码。

三、真实用途
- 大数据: 把内部的 SQL 查询、指标计算封装成 MCP 工具，大模型就能按需取数。
- 数据分析: 工具描述里的参数 Schema 决定了模型会不会传错参数，这是数据工具的关键。
- AI Agent / RAG: 知识库检索本身就可以做成一个 search 工具，Agent 通过 tools/call 调用。
- 全栈开发: 工具注册 + 参数校验 + 统一错误返回，就是后端 API 网关的基本形态。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

PROTOCOL_VERSION = '2024-11-05'  # MCP 协议版本号（学习用，以官方规范为准）
ERROR_METHOD_NOT_FOUND = -32601
ERROR_INVALID_PARAMS = -32602


@dataclass
class Tool:
    """一个可被调用的工具：名字、说明、参数 Schema 与真正执行的函数。"""

    name: str
    description: str
    input_schema: dict[str, Any]
    func: Callable[..., Any]


@dataclass
class MiniMCPServer:
    """迷你服务端：tools 字典保存所有已注册工具。"""

    name: str = 'mini-mcp-server'
    tools: dict[str, Tool] = field(default_factory=dict)

    def tool(self, name: str, description: str, input_schema: dict[str, Any]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """装饰器：@server.tool(...) 把普通函数注册为 MCP 工具。"""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[name] = Tool(name, description, input_schema, func)
            return func  # 原函数不变，依然可以直接调用

        return decorator

    def handle(self, text: str) -> str | None:
        """处理一条收到的 JSON 文本；通知返回 None（不需要回复）。"""
        try:
            message = json.loads(text)
        except json.JSONDecodeError:
            return json.dumps({'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': '解析失败'}}, ensure_ascii=False)

        request_id = message.get('id')
        method = message.get('method', '')
        params = message.get('params', {})

        if request_id is None:  # 没有 id 就是通知，例如 notifications/initialized
            return None

        try:
            result = self._dispatch(method, params)
        except KeyError as exc:  # 未知工具 / 缺少参数等，统一转为参数错误
            return self._error(request_id, ERROR_INVALID_PARAMS, str(exc))
        except TypeError as exc:  # 多余参数或类型不对，Python 调用时会抛 TypeError
            return self._error(request_id, ERROR_INVALID_PARAMS, f'参数错误: {exc}')
        except LookupError:
            return self._error(request_id, ERROR_METHOD_NOT_FOUND, f'方法不存在: {method}')
        return json.dumps({'jsonrpc': '2.0', 'id': request_id, 'result': result}, ensure_ascii=False)

    def _dispatch(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """根据 method 分发到对应处理逻辑。"""
        if method == 'initialize':
            return {
                'protocolVersion': PROTOCOL_VERSION,
                'capabilities': {'tools': {}},  # 只声明支持工具
                'serverInfo': {'name': self.name, 'version': '0.1.0'},
            }
        if method == 'tools/list':
            return {
                'tools': [
                    {'name': t.name, 'description': t.description, 'inputSchema': t.input_schema}
                    for t in self.tools.values()
                ]
            }
        if method == 'tools/call':
            return self._call_tool(params)
        raise LookupError(method)  # 交给上层转为 -32601

    def _call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        """执行工具：先校验必填参数，再调用函数，最后包装成 content 列表。"""
        tool = self.tools[params['name']]  # 工具不存在时抛出 KeyError
        arguments = params.get('arguments', {})
        for required in tool.input_schema.get('required', []):
            if required not in arguments:
                raise KeyError(f'缺少必填参数: {required}')
        output = tool.func(**arguments)
        return {'content': [{'type': 'text', 'text': str(output)}], 'isError': False}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> str:
        """统一生成错误响应。"""
        return json.dumps({'jsonrpc': '2.0', 'id': request_id, 'error': {'code': code, 'message': message}}, ensure_ascii=False)


def build_demo_server() -> MiniMCPServer:
    """构造一个带三个示例工具的服务端。"""
    server = MiniMCPServer()

    @server.tool('add', '计算两个整数的和', {
        'type': 'object',
        'properties': {'a': {'type': 'integer'}, 'b': {'type': 'integer'}},
        'required': ['a', 'b'],
    })
    def add(a: int, b: int) -> int:
        return a + b

    @server.tool('echo', '原样返回输入文本', {
        'type': 'object',
        'properties': {'text': {'type': 'string'}},
        'required': ['text'],
    })
    def echo(text: str) -> str:
        return text

    @server.tool('word_count', '统计英文单词数量', {
        'type': 'object',
        'properties': {'text': {'type': 'string'}},
        'required': ['text'],
    })
    def word_count(text: str) -> int:
        return len(text.split())

    return server


def run_tests() -> None:
    """自动化断言测试：覆盖握手、列表、调用、错误与通知。"""
    server = build_demo_server()

    # 1. initialize：返回协议版本与 tools 能力
    init = json.loads(server.handle(json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}})))
    assert init['result']['protocolVersion'] == PROTOCOL_VERSION
    assert 'tools' in init['result']['capabilities']

    # 2. tools/list：三个工具都在，且带 inputSchema
    listed = json.loads(server.handle(json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})))
    names = [t['name'] for t in listed['result']['tools']]
    assert names == ['add', 'echo', 'word_count']
    assert 'inputSchema' in listed['result']['tools'][0]

    # 3. tools/call：正常调用
    call = json.loads(server.handle(json.dumps({
        'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
        'params': {'name': 'add', 'arguments': {'a': 2, 'b': 3}},
    })))
    assert call['result']['content'][0]['text'] == '5'
    assert call['id'] == 3  # 响应 id 与请求一致

    # 4. 未知方法 -> -32601
    unknown = json.loads(server.handle(json.dumps({'jsonrpc': '2.0', 'id': 4, 'method': 'no/such'})))
    assert unknown['error']['code'] == ERROR_METHOD_NOT_FOUND

    # 5. 未知工具 -> -32602；缺少必填参数 -> -32602
    bad_tool = json.loads(server.handle(json.dumps({
        'jsonrpc': '2.0', 'id': 5, 'method': 'tools/call', 'params': {'name': 'ghost', 'arguments': {}},
    })))
    assert bad_tool['error']['code'] == ERROR_INVALID_PARAMS
    missing = json.loads(server.handle(json.dumps({
        'jsonrpc': '2.0', 'id': 6, 'method': 'tools/call', 'params': {'name': 'add', 'arguments': {'a': 1}},
    })))
    assert missing['error']['code'] == ERROR_INVALID_PARAMS and '缺少必填参数' in missing['error']['message']

    # 5b. 多余参数 -> -32602，服务端不能因此崩溃
    extra = json.loads(server.handle(json.dumps({
        'jsonrpc': '2.0', 'id': 8, 'method': 'tools/call',
        'params': {'name': 'add', 'arguments': {'a': 1, 'b': 2, 'c': 3}},
    })))
    assert extra['error']['code'] == ERROR_INVALID_PARAMS

    # 6. 通知（无 id）不返回任何内容
    assert server.handle(json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'})) is None

    # 7. 非法 JSON 返回解析错误，而不是崩溃
    parse_error = json.loads(server.handle('{坏掉的'))
    assert parse_error['error']['code'] == -32700

    # 8. 中文参数与工具描述正常往返
    word = json.loads(server.handle(json.dumps({
        'jsonrpc': '2.0', 'id': 7, 'method': 'tools/call',
        'params': {'name': 'echo', 'arguments': {'text': '你好 MCP'}},
    })))
    assert word['result']['content'][0]['text'] == '你好 MCP'

    print('✅ 迷你 MCP 服务端所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 迷你 MCP 服务端 {'*' * 12}", sep='', end='\n\n')
    server = build_demo_server()
    request = json.dumps({
        'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
        'params': {'name': 'word_count', 'arguments': {'text': 'hello mcp world'}},
    })
    print('请求:', request)
    print('响应:', server.handle(request))
    run_tests()


if __name__ == '__main__':
    bootstrap()
