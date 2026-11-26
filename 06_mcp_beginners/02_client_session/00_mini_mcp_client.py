"""
[主题]: 迷你 MCP 客户端 (握手 initialize / 发现工具 tools/list / 调用工具 tools/call / 请求-响应匹配)
[来源]: microsoft/mcp-for-beginners 第 4 章「MCP 客户端与会话」(本文件为自行重写的学习版，不依赖官方 SDK)
[难度]: Medium
[前置知识]: 06_mcp_beginners/01_tool_server (迷你服务端)、importlib、异常处理

一、主题说明
客户端（通常是 Cursor、Claude Desktop 或你自己的 Agent）负责：
1. 先发 initialize 握手，再发 notifications/initialized 通知，会话才算建立；
2. 用 tools/list 发现服务端有哪些工具，把描述交给大模型选择；
3. 用 tools/call 执行工具，并按 id 找到对应的响应；
4. 收到 error 时抛出异常，而不是把错误当成正常结果继续使用。
本文件通过函数直接相连模拟“传输层”（真实场景是 stdio 或 HTTP），重点学习消息的收发流程。

二、解法对比（以「拿到工具执行结果」为例）
1. 直观版 call_naive: 直接取 response['result']，错误时会 KeyError，原因难以排查。
   - 时间复杂度 O(1)，但对错误不友好。
2. 进阶版 MiniMCPClient.request: 校验 id 一致、检查 error 字段并抛出带错误码的 RuntimeError。
   - 时间复杂度 O(消息长度)，空间复杂度 O(消息长度)

三、真实用途
- 大数据: 数据平台的调度器调用外部查询服务时，同样需要会话、超时与错误码处理。
- 数据分析: Agent 通过 MCP 客户端调用指标工具，错误要能清楚地反馈给模型或用户。
- AI Agent / RAG: 工具调用失败时，把错误信息作为 observation 回传给模型，让它自己纠正。
- 全栈开发: 前端或后端 SDK 封装的 API 客户端，都应该做握手、统一异常与超时。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Any


def load_server_module() -> ModuleType:
    """通过文件路径加载服务端模块：目录名以数字开头，无法直接 import，这里用 importlib 动态加载。"""
    server_path = Path(__file__).resolve().parent.parent / '01_tool_server' / '00_mini_mcp_server.py'
    spec = importlib.util.spec_from_file_location('mini_mcp_server', server_path)
    if spec is None or spec.loader is None:
        raise ImportError(f'无法加载服务端文件: {server_path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules['mini_mcp_server'] = module  # 先注册再执行，dataclass 解析注解时需要它
    spec.loader.exec_module(module)
    return module


class MiniMCPClient:
    """迷你客户端：transport 是一个“把文本发出去、拿回文本”的函数，相当于传输层。"""

    def __init__(self, transport: Callable[[str], str | None]) -> None:
        self._transport = transport
        self._next_id = 1  # 每次请求递增，用来匹配响应
        self.initialized = False

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """发送一次请求并等待对应 id 的响应，返回 result；出错时抛出 RuntimeError。"""
        request_id = self._next_id
        self._next_id += 1
        message: dict[str, Any] = {'jsonrpc': '2.0', 'id': request_id, 'method': method}
        if params is not None:
            message['params'] = params

        raw = self._transport(json.dumps(message, ensure_ascii=False))
        if raw is None:
            raise RuntimeError(f'服务端没有回复: {method}')
        response = json.loads(raw)
        if response.get('id') != request_id:  # id 不一致说明响应错配，不能直接使用
            raise RuntimeError(f'响应 id 不匹配: 期望 {request_id}，收到 {response.get("id")}')
        if 'error' in response:  # 服务端返回的错误必须明确抛出
            error = response['error']
            raise RuntimeError(f"错误 {error['code']}: {error['message']}")
        return response['result']

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        """通知没有 id，服务端不会回复，因此这里不等待任何返回值。"""
        message: dict[str, Any] = {'jsonrpc': '2.0', 'method': method}
        if params is not None:
            message['params'] = params
        self._transport(json.dumps(message, ensure_ascii=False))

    def initialize(self) -> dict[str, Any]:
        """握手：先 initialize 请求，再发 initialized 通知，之后会话才可用。"""
        result = self.request('initialize', {'protocolVersion': '2024-11-05', 'clientInfo': {'name': 'demo-client'}})
        self.notify('notifications/initialized')
        self.initialized = True
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        """获取工具列表；未握手时拒绝执行，避免跳过协议流程。"""
        self._ensure_initialized()
        return self.request('tools/list')['tools']

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """调用工具并返回第一段文本结果。"""
        self._ensure_initialized()
        result = self.request('tools/call', {'name': name, 'arguments': arguments})
        return result['content'][0]['text']

    def _ensure_initialized(self) -> None:
        if not self.initialized:
            raise RuntimeError('请先调用 initialize() 完成握手')


def build_client() -> MiniMCPClient:
    """创建客户端：把服务端的 handle 方法直接当作传输层。"""
    module = load_server_module()
    server = module.build_demo_server()
    return MiniMCPClient(transport=server.handle)


def run_tests() -> None:
    """自动化断言测试：覆盖握手、发现、调用、错误与未握手保护。"""
    # 1. 未握手直接调用必须失败
    not_ready = MiniMCPClient(transport=lambda text: None)
    try:
        not_ready.list_tools()
    except RuntimeError as exc:
        assert '请先调用 initialize' in str(exc)
    else:
        raise AssertionError('未握手不能列出工具')

    # 2. 完整流程：握手 -> 列出工具 -> 调用 add
    client = build_client()
    info = client.initialize()
    assert info['serverInfo']['name'] == 'mini-mcp-server'
    tools = client.list_tools()
    assert [t['name'] for t in tools] == ['add', 'echo', 'word_count']
    assert client.call_tool('add', {'a': 20, 'b': 22}) == '42'
    assert client.call_tool('word_count', {'text': 'a b c'}) == '3'

    # 3. 服务端返回错误时，客户端抛出带错误码的异常
    try:
        client.call_tool('ghost', {})
    except RuntimeError as exc:
        assert '-32602' in str(exc)
    else:
        raise AssertionError('未知工具必须抛出异常')

    # 4. 请求 id 递增：每次请求都使用新的 id
    before = client._next_id
    client.call_tool('echo', {'text': '你好'})
    assert client._next_id == before + 1

    # 5. 响应错配：传输层返回了别的 id，客户端必须拒绝
    def wrong_id_transport(text: str) -> str:
        return json.dumps({'jsonrpc': '2.0', 'id': 999, 'result': {}})

    broken = MiniMCPClient(transport=wrong_id_transport)
    broken.initialized = True
    try:
        broken.list_tools()
    except RuntimeError as exc:
        assert 'id 不匹配' in str(exc)
    else:
        raise AssertionError('响应 id 错配必须报错')

    print('✅ 迷你 MCP 客户端所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 迷你 MCP 客户端 {'*' * 12}", sep='', end='\n\n')
    client = build_client()
    print('握手结果:', client.initialize())
    print('可用工具:', [t['name'] for t in client.list_tools()])
    print('add(2, 3) =', client.call_tool('add', {'a': 2, 'b': 3}))
    run_tests()


if __name__ == '__main__':
    bootstrap()
