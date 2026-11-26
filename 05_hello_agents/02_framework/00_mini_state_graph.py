"""
[主题]: 迷你智能体框架：状态图 (StateGraph)，节点 / 边 / 条件路由 / 循环保护
[来源]: datawhalechina/hello-agents 第六、七章「框架开发」(本文件为自行重写的标准库学习版，思想与 LangGraph 一致)
[难度]: Hard
[前置知识]: 05_hello_agents/01_planning (计划与执行)、函数作为参数、dict 与 Callable、异常

一、主题说明
智能体一旦变复杂，“if 嵌套 while”会难以维护。框架的核心思想只有三点：
1. 状态 (State): 所有节点共享一个字典，每个节点读取它、更新它，然后返回；
2. 节点 (Node): 一个只做一件事的函数（分类、计算、复核……）；
3. 边 (Edge): 决定下一个节点是谁。普通边是固定的；条件边由路由函数根据状态决定去向，这就是“分支”与“循环”的来源。
为了防止条件边造成死循环（烧光 Token），运行时必须设置最大步数。

二、解法对比（以「分类后选择计算或闲聊，计算失败则重试」为例）
1. 直观版 run_with_if: 用一大段 if/while 嵌套写流程，每加一个分支都要改动主逻辑。
   - 时间复杂度 O(执行步数)，但流程不可视化，也难以复用。
2. 进阶版 StateGraph.run: 流程用“节点 + 边”声明，运行器统一调度，并记录执行轨迹（trace）。
   - 时间复杂度 O(执行步数)，新增节点只需注册，不改运行器，并且能看到每一步走了哪里。

三、真实用途
- 大数据: 数据管道的编排（Airflow、Dagster）同样是“节点 + 依赖边 + 条件分支”。
- 数据分析: 报表生成流程“取数 -> 校验 -> 不通过则重算”就是带循环的状态图。
- AI Agent / RAG: LangGraph 等框架的底层正是这种结构，理解它能快速上手任何 Agent 框架。
- 全栈开发: 订单、审批、退款等业务状态机，本质也是状态图，路由错误是线上事故的常见来源。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

State = dict[str, Any]
Node = Callable[[State], State]
Router = Callable[[State], str]
END = '__end__'


class StateGraph:
    """状态图：注册节点与边，然后从入口开始运行，直到到达 END。"""

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, str] = {}  # 普通边：src -> dst
        self.conditional: dict[str, tuple[Router, dict[str, str]]] = {}  # 条件边：src -> (路由函数, 结果到节点的映射)
        self.entry: str | None = None

    def add_node(self, name: str, fn: Node) -> None:
        """注册节点。"""
        self.nodes[name] = fn

    def add_edge(self, src: str, dst: str) -> None:
        """注册普通边：执行完 src 后固定进入 dst。"""
        self.edges[src] = dst

    def add_conditional_edges(self, src: str, router: Router, mapping: dict[str, str]) -> None:
        """注册条件边：路由函数返回一个键，再通过 mapping 找到下一个节点。"""
        self.conditional[src] = (router, mapping)

    def set_entry_point(self, name: str) -> None:
        """设置入口节点。"""
        self.entry = name

    def run(self, state: State, max_steps: int = 10) -> tuple[State, list[str]]:
        """运行图：返回最终状态与经过的节点轨迹。超过 max_steps 仍未结束则报错。"""
        if self.entry is None:
            raise RuntimeError('没有设置入口节点')
        current = self.entry
        trace: list[str] = []
        for _ in range(max_steps):
            if current == END:
                return state, trace
            if current not in self.nodes:
                raise KeyError(f'未注册的节点: {current}')
            trace.append(current)
            state = self.nodes[current](state)  # 执行节点，拿到更新后的状态
            if current in self.conditional:  # 条件边优先
                router, mapping = self.conditional[current]
                current = mapping[router(state)]
            else:
                current = self.edges.get(current, END)  # 没有出边就结束
        raise RuntimeError(f'超过最大步数 {max_steps}，可能存在死循环，轨迹: {trace}')


def classify(state: State) -> State:
    """节点：判断问题类型。含数字与运算符的是计算题，否则是闲聊。"""
    state['kind'] = 'math' if re.search(r'\d\s*[+\-*/]\s*\d', state['question']) else 'chat'
    return state


def calculate(state: State) -> State:
    """节点：计算 “a op b”。解析失败时不抛异常，而是记录 answer 为 None，交给复核节点处理。"""
    match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', state['question'])
    state['attempts'] = state.get('attempts', 0) + 1
    if match is None:
        state['answer'] = None
        return state
    a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
    results = {'+': a + b, '-': a - b, '*': a * b, '/': a / b if b else None}
    state['answer'] = results[op]
    return state


def chat(state: State) -> State:
    """节点：闲聊类问题的固定回复。"""
    state['answer'] = '你好，我可以帮你做简单的四则运算。'
    return state


def review(state: State) -> State:
    """节点：复核结果，这里只做记录，路由决定是否重试。"""
    state['reviewed'] = True
    return state


def build_graph() -> StateGraph:
    """组装图：classify -> (calculate | chat) -> review，计算结果为空时回到 calculate 重试（最多 2 次）。"""
    graph = StateGraph()
    graph.add_node('classify', classify)
    graph.add_node('calculate', calculate)
    graph.add_node('chat', chat)
    graph.add_node('review', review)
    graph.set_entry_point('classify')
    graph.add_conditional_edges('classify', lambda s: s['kind'], {'math': 'calculate', 'chat': 'chat'})
    graph.add_edge('calculate', 'review')
    graph.add_edge('chat', 'review')
    graph.add_conditional_edges(
        'review',
        # 注意：闲聊分支不会设置 attempts，所以要用 get 给默认值，否则会 KeyError
        lambda s: 'retry' if s['answer'] is None and s.get('attempts', 0) < 2 else 'done',
        {'retry': 'calculate', 'done': END},
    )
    return graph


def run_tests() -> None:
    """自动化断言测试：覆盖分支、计算、闲聊、重试循环与死循环保护。"""
    graph = build_graph()

    # 1. 计算分支：轨迹应为 classify -> calculate -> review
    state, trace = graph.run({'question': '12 * 3'})
    assert state['answer'] == 36 and state['kind'] == 'math'
    assert trace == ['classify', 'calculate', 'review']

    # 2. 闲聊分支：不会经过 calculate
    state, trace = graph.run({'question': '你好'})
    assert state['kind'] == 'chat' and 'calculate' not in trace
    assert state['reviewed'] is True

    # 3. 没有数字的问题不是计算题，走闲聊分支，从不进入 calculate，也就没有 attempts
    state, trace = graph.run({'question': '请帮我算一下'})
    assert state['kind'] == 'chat' and 'attempts' not in state
    assert trace == ['classify', 'chat', 'review']

    # 4. 除以零：answer 为 None，复核后重试两次，然后结束（不会死循环）
    state, trace = graph.run({'question': '1 / 0'})
    assert state['answer'] is None and state['attempts'] == 2
    assert trace.count('calculate') == 2

    # 5. 死循环保护：一个永远回到自己的图会在 max_steps 后报错
    looping = StateGraph()
    looping.add_node('spin', lambda s: s)
    looping.set_entry_point('spin')
    looping.add_edge('spin', 'spin')
    try:
        looping.run({}, max_steps=5)
    except RuntimeError as exc:
        assert '死循环' in str(exc)
    else:
        raise AssertionError('死循环必须被 max_steps 拦住')

    # 6. 边界：没有入口节点不能运行
    try:
        StateGraph().run({})
    except RuntimeError:
        pass
    else:
        raise AssertionError('没有入口必须报错')

    print('✅ 迷你状态图框架所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 迷你状态图框架 {'*' * 12}", sep='', end='\n\n')
    graph = build_graph()
    for question in ['8 + 5', '你好', '7 / 0']:
        state, trace = graph.run({'question': question})
        print(f'问题 {question!r}: 轨迹 {trace} -> 答案 {state["answer"]}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
