"""
[主题]: ReAct 智能体循环 (Reason + Act)
[来源]: datawhalechina/hello-agents 第四章「智能体经典范式构建」
[难度]: Medium
[前置知识]: chapter04 (分支)、dict、re 正则、dataclass

一、主题说明
ReAct = Thought(思考) -> Action(调用工具) -> Observation(观察结果) 反复循环，直到给出 Final Answer。
为了离线可运行，这里用「规则版假 LLM」FakeLLM 代替真实大模型，它按固定规则输出 ReAct 文本。

二、解法对比
1. 直观版 run_react_basic:
   - while/for 循环 + 正则解析，最容易看懂流程。
   - 缺点: 遇到未知工具会直接 KeyError 崩溃，也没有记录每一步的轨迹。
   - 时间复杂度 O(步数)，空间复杂度 O(步数)
2. 进阶版 run_react_traced:
   - 用 dataclass 记录每一步轨迹；未知工具返回「错误观察」交给模型自行纠正，而不是崩溃；
   - 严格限制 max_steps，防止模型死循环烧 Token。
   - 时间复杂度 O(步数)，空间复杂度 O(步数)

三、真实用途
- AI Agent: 所有「模型想一步、调一次工具、看结果再想」的智能体都是这个骨架。
- 全栈开发: max_steps 与错误观察是线上 Agent 控制成本和稳定性的第一道护栏。
- 数据分析: 让 Agent 调用 SQL / Pandas 工具时，同样靠这套循环串联多步。
"""

from __future__ import annotations

import ast
import operator
import re
from collections.abc import Callable
from dataclasses import dataclass

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

ACTION_RE = re.compile(r'Action:\s*(\w+)\s*\nAction Input:\s*(.+)')
FINAL_RE = re.compile(r'Final Answer:\s*(.+)')


def safe_calc(expr: str) -> int | float:
    """安全计算器：用 ast 只放行 + - * / 与数字，避免直接 eval 带来的代码注入。"""

    def evaluate(node: ast.AST) -> int | float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        raise ValueError(f'不支持的表达式: {expr}')

    return evaluate(ast.parse(expr.strip(), mode='eval'))


class FakeLLM:
    """规则版假 LLM: 没有观察结果时先调用 calculator，拿到结果后给出最终答案。"""

    def __call__(self, question: str, observations: list[str]) -> str:
        if observations:
            return f'Thought: 已经得到结果\nFinal Answer: 结果是 {observations[-1]}'
        found = re.search(r'[\d(][\d+\-*/(). ]*[\d)]', question)
        expr = found.group(0).strip() if found else '0'
        return f'Thought: 需要先计算\nAction: calculator\nAction Input: {expr}'


@dataclass
class Step:
    """一步 ReAct 的完整轨迹，方便调试与展示。"""

    action: str
    action_input: str
    observation: str


def run_react_basic(
    question: str,
    llm: Callable[[str, list[str]], str],
    tools: dict[str, Callable[[str], object]],
    max_steps: int = 5,
) -> str:
    """直观版：循环调用模型，解析 Action 并执行工具。"""
    observations: list[str] = []
    for _ in range(max_steps):
        reply = llm(question, observations)
        final = FINAL_RE.search(reply)
        if final:  # 模型已经给出最终答案
            return final.group(1).strip()
        action = ACTION_RE.search(reply)
        if action is None:
            return '解析失败'
        name, arg = action.group(1), action.group(2).strip()
        observations.append(str(tools[name](arg)))  # 未知工具会在这里 KeyError
    return '超过最大步数'


def run_react_traced(
    question: str,
    llm: Callable[[str, list[str]], str],
    tools: dict[str, Callable[[str], object]],
    max_steps: int = 5,
) -> tuple[str, list[Step]]:
    """进阶版：记录轨迹，未知工具和工具异常都变成「错误观察」。"""
    observations: list[str] = []
    steps: list[Step] = []
    for _ in range(max_steps):
        reply = llm(question, observations)
        final = FINAL_RE.search(reply)
        if final:
            return final.group(1).strip(), steps
        action = ACTION_RE.search(reply)
        if action is None:
            return '解析失败', steps
        name, arg = action.group(1), action.group(2).strip()
        if name not in tools:
            observation = f'错误: 未知工具 {name}'
        else:
            try:
                observation = str(tools[name](arg))
            except ValueError as exc:  # 工具参数错误交给模型自行纠正
                observation = f'错误: {exc}'
        steps.append(Step(name, arg, observation))
        observations.append(observation)
    return '超过最大步数', steps


def run_tests() -> None:
    """自动化断言测试。"""
    tools = {'calculator': safe_calc}
    question = '请计算 (3+4)*5 的结果'

    assert safe_calc('(3+4)*5') == 35
    assert safe_calc('7/2') == 3.5
    assert safe_calc('-2+5') == 3
    try:
        safe_calc('__import__("os")')
    except ValueError:
        pass
    else:
        raise AssertionError('危险表达式必须被拒绝')

    assert run_react_basic(question, FakeLLM(), tools) == '结果是 35'

    answer, steps = run_react_traced(question, FakeLLM(), tools)
    assert answer == '结果是 35'
    assert len(steps) == 1 and steps[0].action == 'calculator' and steps[0].observation == '35'

    def stubborn_llm(_q: str, _obs: list[str]) -> str:
        return 'Thought: 再试一次\nAction: search\nAction Input: x'

    answer, steps = run_react_traced('x', stubborn_llm, tools, max_steps=3)
    assert answer == '超过最大步数' and len(steps) == 3
    assert steps[0].observation == '错误: 未知工具 search'
    print('✅ ReAct 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} ReAct 智能体循环 {'*' * 12}", sep='', end='\n\n')
    answer, steps = run_react_traced('请计算 (3+4)*5 的结果', FakeLLM(), {'calculator': safe_calc})
    for index, step in enumerate(steps, start=1):
        print(f'第 {index} 步: 调用 {step.action}({step.action_input}) -> {step.observation}')
    print(f'最终答案: {answer}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
