"""
[主题]: 工具调用路由 (Tool Calling) 与自我纠正重试
[来源]: NirDiamant/GenAI_Agents 中「带工具的 Agent」类案例的共性骨架
[难度]: Medium
[前置知识]: json、dict、dataclass、isinstance、try/except

一、主题说明
大模型输出的工具调用是一段 JSON：{"tool": "...", "arguments": {...}}。
程序必须像对待用户输入一样对待它：先解析、再按 schema 校验、最后才执行。
校验失败时把**结构化的错误信息**回传给模型，模型通常能自己改对，这就是「自我纠正」。

二、解法对比
1. 直观版 dispatch_basic:
   - json.loads 之后直接调用函数，参数缺失或类型错就抛异常崩溃。
2. 进阶版 dispatch + run_agent:
   - 先校验工具是否存在、必填参数是否齐全、参数类型是否正确；
   - 返回 {'ok': False, 'error': ...} 而不是抛异常，并支持最多 max_retries 次重试。
   - 时间复杂度 O(参数个数)，空间复杂度 O(1)

三、真实用途
- AI Agent: 线上 Agent 最常见的故障就是参数不合法，校验 + 回传错误能显著提升成功率。
- 全栈开发: 与 FastAPI 的请求校验同理，是防止提示注入触发危险调用的屏障。
- 大数据: 让 Agent 调 SQL / 调度工具时，参数校验能避免误删误改。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

WEATHER = {'长沙': '晴 25°C', '北京': '多云 18°C'}


@dataclass(frozen=True)
class ToolSpec:
    """工具说明书：名字、参数类型、必填项、实际函数。"""

    name: str
    params: dict[str, type | tuple[type, ...]]
    required: tuple[str, ...]
    func: Callable[..., Any]


def get_weather(city: str) -> str:
    return f'{city}: {WEATHER.get(city, "暂无数据")}'


def add(a: float, b: float) -> float:
    return a + b


REGISTRY = {
    'get_weather': ToolSpec('get_weather', {'city': str}, ('city',), get_weather),
    'add': ToolSpec('add', {'a': (int, float), 'b': (int, float)}, ('a', 'b'), add),
}


def dispatch_basic(raw_json: str) -> Any:
    """直观版：不做任何校验，出错就崩溃。"""
    call = json.loads(raw_json)
    return REGISTRY[call['tool']].func(**call['arguments'])


def validate_call(spec: ToolSpec, arguments: dict[str, Any]) -> list[str]:
    """按 schema 校验参数，返回错误列表。"""
    errors = [f'缺少必填参数 {name}' for name in spec.required if name not in arguments]
    for name, value in arguments.items():
        if name not in spec.params:
            errors.append(f'未知参数 {name}')
            continue
        # bool 是 int 的子类，数字参数不应接受 True / False
        if isinstance(value, bool) or not isinstance(value, spec.params[name]):
            errors.append(f'参数 {name} 类型错误: 期望 {spec.params[name]}，实际 {type(value).__name__}')
    return errors


def dispatch(registry: dict[str, ToolSpec], raw_json: str) -> dict[str, Any]:
    """进阶版：解析 -> 校验 -> 执行，错误都变成结构化结果。"""
    try:
        call = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {'ok': False, 'error': f'JSON 解析失败: {exc.msg}'}
    if not isinstance(call, dict) or 'tool' not in call:
        return {'ok': False, 'error': '缺少 tool 字段'}
    spec = registry.get(call['tool'])
    if spec is None:
        return {'ok': False, 'error': f'未知工具 {call["tool"]}'}
    arguments = call.get('arguments', {})
    if not isinstance(arguments, dict):
        return {'ok': False, 'error': 'arguments 必须是对象'}
    errors = validate_call(spec, arguments)
    if errors:
        return {'ok': False, 'error': '; '.join(errors)}
    return {'ok': True, 'result': spec.func(**arguments)}


def run_agent(
    llm: Callable[[str, str | None], str],
    registry: dict[str, ToolSpec],
    question: str,
    max_retries: int = 2,
) -> tuple[dict[str, Any], int]:
    """带自我纠正的 Agent：失败时把错误回传给模型重试，返回 (结果, 尝试次数)。"""
    error: str | None = None
    result: dict[str, Any] = {'ok': False, 'error': '尚未调用'}
    for attempt in range(1, max_retries + 2):
        result = dispatch(registry, llm(question, error))
        if result['ok']:
            return result, attempt
        error = result['error']
    return result, max_retries + 1


def fake_llm(question: str, error: str | None) -> str:
    """假 LLM：第一次把 city 写成数字，收到错误反馈后改正。"""
    if error is None:
        return '{"tool": "get_weather", "arguments": {"city": 123}}'
    return '{"tool": "get_weather", "arguments": {"city": "长沙"}}'


def run_tests() -> None:
    """自动化断言测试。"""
    assert dispatch_basic('{"tool": "add", "arguments": {"a": 1, "b": 2}}') == 3
    try:
        dispatch_basic('{"tool": "add", "arguments": {"a": 1}}')
    except TypeError:
        pass
    else:
        raise AssertionError('直观版缺参数应当崩溃，这正是它的缺点')

    ok = dispatch(REGISTRY, '{"tool": "add", "arguments": {"a": 1.5, "b": 2}}')
    assert ok == {'ok': True, 'result': 3.5}
    assert dispatch(REGISTRY, 'not json')['error'].startswith('JSON 解析失败')
    assert dispatch(REGISTRY, '[]')['error'] == '缺少 tool 字段'
    assert dispatch(REGISTRY, '{"tool": "rm", "arguments": {}}')['error'] == '未知工具 rm'
    assert '缺少必填参数 b' in dispatch(REGISTRY, '{"tool": "add", "arguments": {"a": 1}}')['error']
    assert '类型错误' in dispatch(REGISTRY, '{"tool": "add", "arguments": {"a": true, "b": 1}}')['error']
    assert '未知参数 x' in dispatch(REGISTRY, '{"tool": "get_weather", "arguments": {"city": "a", "x": 1}}')['error']

    result, attempts = run_agent(fake_llm, REGISTRY, '长沙天气怎么样')
    assert result == {'ok': True, 'result': '长沙: 晴 25°C'} and attempts == 2

    def hopeless_llm(_q: str, _e: str | None) -> str:
        return '{"tool": "get_weather", "arguments": {}}'

    result, attempts = run_agent(hopeless_llm, REGISTRY, 'x', max_retries=2)
    assert result['ok'] is False and attempts == 3
    print('✅ 工具调用路由所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 工具调用路由与自我纠正 {'*' * 12}", sep='', end='\n\n')
    result, attempts = run_agent(fake_llm, REGISTRY, '长沙天气怎么样')
    print(f'尝试 {attempts} 次后得到: {result}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
