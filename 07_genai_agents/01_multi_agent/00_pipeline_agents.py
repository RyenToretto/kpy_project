"""
[主题]: 多 Agent 流水线：研究员 -> 写手 -> 审稿人（不通过则返工）
[来源]: NirDiamant/GenAI_Agents 中多智能体协作类案例的共性骨架
[难度]: Medium
[前置知识]: dict、list、dataclass、Protocol、函数式组合

一、主题说明
多 Agent 协作的本质：每个 Agent 只做一件事，通过共享的 state(字典) 传递成果，
由编排器 (Orchestrator) 决定执行顺序，并在审稿不通过时让写手返工。
这里全部用规则函数模拟，保证离线、可重复。

二、解法对比
1. 直观版 pipeline_basic:
   - 三个函数顺序调用，写死流程，审稿不通过也无法返工。
2. 进阶版 Orchestrator:
   - 所有 Agent 实现同一个 run(state) -> state 接口，可随意替换与增减；
   - 记录执行轨迹 trace；审稿不通过时带着意见让写手重写，最多 max_rounds 轮。
   - 时间复杂度 O(轮数 * Agent 数)，空间复杂度 O(轨迹长度)

三、真实用途
- AI Agent: 研报生成、代码审查、客服质检都是「生产者 + 检查者」的闭环。
- 全栈开发: 每个 Agent 就是一个可独立测试的服务，编排器相当于工作流引擎。
- 大数据: 与 Airflow 的 DAG 同理，只是节点换成了会思考的 Agent。
"""

from __future__ import annotations

from typing import Any, Protocol

State = dict[str, Any]

KNOWLEDGE = {
    'rag': 'RAG 先检索再生成，可以减少幻觉',
    'agent': 'Agent 能规划步骤并调用工具',
}


def research(state: State) -> State:
    """研究员：根据主题从知识库里取事实，并附上来源编号。"""
    topic = state['topic'].lower()
    facts = [(text, f'知识库#{key}') for key, text in KNOWLEDGE.items() if key in topic]
    return {**state, 'facts': facts}


def write(state: State) -> State:
    """写手：把事实写成段落。第一次不标注来源，收到审稿意见后才补上。"""
    with_source = bool(state.get('feedback'))
    lines = [f'{text}[{source}]' if with_source else text for text, source in state['facts']]
    return {**state, 'draft': '；'.join(lines)}


def review(state: State) -> State:
    """审稿人：每条事实都必须带 [来源]，否则驳回并给出意见。"""
    missing = '[' not in state['draft']
    return {
        **state,
        'approved': not missing,
        'feedback': '' if not missing else '每条事实都要标注来源',
    }


def pipeline_basic(topic: str) -> State:
    """直观版：写死顺序，没有返工机制。"""
    return review(write(research({'topic': topic})))


class Agent(Protocol):
    def __call__(self, state: State) -> State: ...


class Orchestrator:
    """编排器：先跑研究员，再让写手和审稿人循环，直到通过或达到上限。"""

    def __init__(self, researcher: Agent, writer: Agent, reviewer: Agent, max_rounds: int = 3) -> None:
        self.researcher, self.writer, self.reviewer = researcher, writer, reviewer
        self.max_rounds = max_rounds

    def run(self, topic: str) -> State:
        state: State = {'topic': topic, 'trace': ['researcher']}
        state = self.researcher(state)
        for round_no in range(1, self.max_rounds + 1):
            state = self.writer(state)
            state['trace'] = [*state['trace'], 'writer']
            state = self.reviewer(state)
            state['trace'] = [*state['trace'], 'reviewer']
            state['rounds'] = round_no
            if state['approved']:
                break
        return state


def run_tests() -> None:
    """自动化断言测试。"""
    basic = pipeline_basic('介绍 RAG 与 Agent')
    assert basic['approved'] is False  # 直观版第一稿没标来源，被驳回却没人返工

    result = Orchestrator(research, write, review).run('介绍 RAG 与 Agent')
    assert result['approved'] is True and result['rounds'] == 2
    assert result['trace'] == ['researcher', 'writer', 'reviewer', 'writer', 'reviewer']
    assert '[知识库#rag]' in result['draft'] and '[知识库#agent]' in result['draft']

    # 没有任何可用事实：审稿永远通过不了，应当在 max_rounds 后停止而不是死循环
    stuck = Orchestrator(research, write, review, max_rounds=2).run('完全无关的主题')
    assert stuck['approved'] is False and stuck['rounds'] == 2

    # Agent 可替换：换一个总是通过的审稿人，只需要 1 轮
    lenient = Orchestrator(research, write, lambda s: {**s, 'approved': True, 'feedback': ''}).run('rag')
    assert lenient['rounds'] == 1
    print('✅ 多 Agent 流水线所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 多 Agent 流水线 {'*' * 12}", sep='', end='\n\n')
    result = Orchestrator(research, write, review).run('介绍 RAG 与 Agent')
    print(f'执行轨迹: {" -> ".join(result["trace"])}')
    print(f'是否通过: {result["approved"]}，共 {result["rounds"]} 轮')
    print(f'最终稿: {result["draft"]}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
