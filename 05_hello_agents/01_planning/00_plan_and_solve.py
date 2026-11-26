"""
[主题]: Plan-and-Solve 智能体范式 (先制定计划，再按步骤执行，并把前一步结果传给后一步)
[来源]: datawhalechina/hello-agents 第四章「Plan-and-Solve」(本文件为自行重写的标准库学习版，规则版假 LLM 代替模型)
[难度]: Medium
[前置知识]: 05_hello_agents/00_agent_basics (ReAct 循环、安全计算器)、列表、字典、dataclass

一、主题说明
ReAct 是“边想边做”，适合探索性任务；Plan-and-Solve 是“先想好再做”，适合步骤清晰的多步问题：
1. Plan（规划）: 模型一次性输出完整步骤列表；
2. Solve（执行）: 按顺序执行每一步，后一步可以引用前一步的结果（如 #1、#2 占位符）；
3. 失败处理: 某一步失败时记录错误并停止，而不是盲目继续，避免后续步骤基于错误数据运行。
规划让整体流程可读、可审计，这是企业级 Agent 更偏好的方式。

二、解法对比（以「完成一个三步的计算任务」为例）
1. 直观版 run_step_by_step: 每一步都重新询问模型“下一步做什么”，每次都要一次模型调用。
   - 模型调用次数 O(步数)，过程难以事先审查。
2. 进阶版 plan_and_solve: 先一次性生成计划，再机械执行，结果可以提前检查。
   - 模型调用次数 = 1（规划），执行阶段不调用模型；步骤间用占位符传递结果。

三、真实用途
- 大数据: 批处理作业的 DAG 通常是先规划、再执行，计划可以提前做资源评估。
- 数据分析: “查数据 -> 清洗 -> 计算指标 -> 出图”这类固定流程，适合 Plan-and-Solve。
- AI Agent / RAG: 复杂问答先拆成检索、比较、汇总三步，比一步到位更稳定。
- 全栈开发: 工单自动化、批量发布等流程，计划阶段的审批能拦住危险操作。
"""

from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass, field

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def safe_calc(expr: str) -> float:
    """安全计算器：只允许数字与 + - * /，用 ast 解析，拒绝一切函数调用与属性访问。"""

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
        raise ValueError(f'不支持的表达式: {expr}')

    return evaluate(ast.parse(expr, mode='eval'))


def make_plan(question: str) -> list[str]:
    """规则版规划器：真实系统中这里是大模型一次性输出的步骤列表。占位符 #1、#2 指向前面步骤的结果。"""
    if question == '先算 (12+8)，再乘以 3，最后减去 6':
        return ['calc: 12 + 8', 'calc: #1 * 3', 'calc: #2 - 6']
    return []


@dataclass
class PlanResult:
    """执行结果：最终答案、每一步的输出，以及失败时的错误信息。"""

    answer: str | None
    step_outputs: list[str] = field(default_factory=list)
    error: str | None = None


def execute_step(step: str, previous: list[str]) -> str:
    """执行单个步骤：先把 #n 占位符替换为第 n 步的结果，再交给对应工具。"""
    action, _, argument = step.partition(':')
    for index, output in enumerate(previous, start=1):  # 占位符替换：#1 -> 第一步的结果
        argument = argument.replace(f'#{index}', output)
    if action.strip() == 'calc':
        result = safe_calc(argument.strip())
        return str(int(result)) if result == int(result) else str(result)
    raise ValueError(f'未知动作: {action}')


def execute_plan(steps: list[str]) -> PlanResult:
    """按顺序执行计划。某一步失败就立即停止，并返回已经完成的步骤与错误原因。"""
    outputs: list[str] = []
    for step in steps:
        try:
            outputs.append(execute_step(step, outputs))
        except (ValueError, ZeroDivisionError) as exc:
            return PlanResult(answer=None, step_outputs=outputs, error=f'步骤失败: {step} ({exc})')
    return PlanResult(answer=outputs[-1] if outputs else None, step_outputs=outputs)


def plan_and_solve(question: str) -> PlanResult:
    """完整流程：先规划，再执行；没有生成计划时直接返回错误。"""
    steps = make_plan(question)
    if not steps:
        return PlanResult(answer=None, error='无法生成计划')
    return execute_plan(steps)


def run_tests() -> None:
    """自动化断言测试：覆盖计划生成、占位符传递、失败停止与安全校验。"""
    # 1. 完整流程：(12+8)*3-6 = 54，中间结果依次为 20、60、54
    result = plan_and_solve('先算 (12+8)，再乘以 3，最后减去 6')
    assert result.error is None
    assert result.step_outputs == ['20', '60', '54']
    assert result.answer == '54'

    # 2. 计划可以事先检查：步骤列表与顺序是固定的
    assert make_plan('先算 (12+8)，再乘以 3，最后减去 6')[1] == 'calc: #1 * 3'

    # 3. 占位符替换：第 2 步使用第 1 步的结果
    assert execute_step('calc: #1 * 2', ['5']) == '10'

    # 4. 没有计划时直接返回错误，不会去执行任何步骤
    no_plan = plan_and_solve('不存在的任务')
    assert no_plan.answer is None and no_plan.error == '无法生成计划'

    # 4b. 失败即停止：第 2 步除以零，第 3 步不应被执行，第 1 步的结果仍然保留
    failed = execute_plan(['calc: 6 + 6', 'calc: #1 / 0', 'calc: #2 + 1'])
    assert failed.answer is None
    assert failed.step_outputs == ['12']
    assert failed.error is not None and '步骤失败' in failed.error

    # 5. 安全计算器拒绝函数调用（与 ReAct 章节一致）
    try:
        safe_calc('__import__("os")')
    except ValueError:
        pass
    else:
        raise AssertionError('危险表达式必须被拒绝')

    # 6. 未知动作报错，而不是静默忽略
    try:
        execute_step('search: 退款', [])
    except ValueError as exc:
        assert '未知动作' in str(exc)
    else:
        raise AssertionError('未知动作必须报错')

    print('✅ Plan-and-Solve 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} Plan-and-Solve {'*' * 12}", sep='', end='\n\n')
    question = '先算 (12+8)，再乘以 3，最后减去 6'
    for index, step in enumerate(make_plan(question), start=1):
        print(f'计划第 {index} 步: {step}')
    result = plan_and_solve(question)
    print(f'每步结果: {result.step_outputs}')
    print(f'最终答案: {result.answer}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
