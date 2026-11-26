"""
[主题]: 智能体记忆与上下文工程 (短期记忆 / 长期记忆检索 / 上下文预算裁剪)
[来源]: datawhalechina/hello-agents 第八、九章「记忆与上下文工程」(本文件为自行重写的标准库学习版)
[难度]: Hard
[前置知识]: 04_protocols 之前的全部内容、dataclass、排序与切片、字典

一、主题说明
模型的上下文窗口是有限的预算，智能体能“记住”什么，取决于往窗口里放什么。上下文工程要解决三个问题：
1. 短期记忆: 最近几轮对话原文，保证当前话题连贯；
2. 长期记忆: 用户偏好、历史事实等，存起来，需要时按相关性检索出来；
3. 预算裁剪: 把系统提示、检索到的记忆、最近对话按优先级装进固定的 Token 预算，超出的从低优先级开始丢弃。
系统提示（规则与身份）是“必须保留”的，不参与裁剪。

二、解法对比（以「把所有历史都塞进上下文」为例）
1. 直观版 build_context_naive: 把全部历史与全部记忆按时间顺序拼接，超出预算就直接截断末尾。
   - 容易把关键的系统提示和最新问题截掉，结果不可控。
2. 进阶版 build_context: 系统提示必留，其余按优先级（检索记忆 > 最近对话）装入，超预算时逐条丢弃低优先级内容。
   - 时间复杂度 O(记忆条数 × 词表)（检索）+ O(条数)（装载），关键信息得到保护。

三、真实用途
- 大数据: 长期用户画像与行为日志的摘要、检索，决定了个性化服务的上限与成本。
- 数据分析: 分析师与 Agent 的多轮对话里，关键结论应存为长期记忆，避免每次重复解释背景。
- AI Agent / RAG: 上下文预算是 Agent 成本与稳定性的核心，超长上下文会让模型“迷失在中间”。
- 全栈开发: 聊天产品的历史消息分页、会员个性化偏好存储，都是这套设计的生产版本。
"""

from __future__ import annotations

from dataclasses import dataclass, field


def estimate_tokens(text: str) -> int:
    """粗略估算 Token：中文约 1 字 1 Token，其余字符约 4 个 1 Token（仅为教学用的近似，真实计费以 tokenizer 为准）。"""
    chinese = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    return chinese + (len(text) - chinese + 3) // 4


@dataclass
class Memory:
    """记忆库：短期窗口保存最近对话，长期列表保存事实，检索时按字符重叠排序。"""

    window: int = 2
    recent: list[str] = field(default_factory=list)
    long_term: list[str] = field(default_factory=list)

    def remember_turn(self, text: str) -> None:
        """记录一轮对话：超出窗口的旧对话被移除（真实系统中会先摘要再存入长期记忆）。"""
        self.recent.append(text)
        if len(self.recent) > self.window:
            self.recent = self.recent[-self.window:]

    def store_fact(self, fact: str) -> None:
        """写入长期记忆：同一条事实不重复保存。"""
        if fact not in self.long_term:
            self.long_term.append(fact)

    def recall(self, query: str, top_k: int = 2) -> list[str]:
        """按字符重叠检索长期记忆，只返回至少有一个字符相关的事实。"""
        query_chars = set(query)
        scored = [(len(query_chars & set(fact)), index, fact) for index, fact in enumerate(self.long_term)]
        scored = [item for item in scored if item[0] > 0]
        scored.sort(key=lambda item: (-item[0], item[1]))  # 重叠多的优先，同分保持写入顺序
        return [fact for _, _, fact in scored[:top_k]]


def build_context(system: str, memory: Memory, question: str, budget: int) -> str:
    """按优先级装配上下文：系统提示必留 > 当前问题必留 > 检索到的记忆 > 最近对话（从新到旧）。"""
    required = [system, f'用户问题: {question}']
    used = sum(estimate_tokens(part) for part in required)
    if used > budget:
        raise ValueError('预算连系统提示与问题都放不下')

    picked: list[str] = []
    candidates = memory.recall(question) + list(reversed(memory.recent))  # 记忆在前，近期对话从新到旧
    for item in candidates:
        cost = estimate_tokens(item)
        if used + cost <= budget:  # 放得下就装入，放不下的低优先级内容直接丢弃
            picked.append(item)
            used += cost
    return '\n'.join([system, *picked, f'用户问题: {question}'])


def build_context_naive(system: str, memory: Memory, question: str, budget: int) -> str:
    """直观版：按时间顺序拼接所有内容，超出预算就从末尾截断（反面教材，会截掉系统提示之后的关键信息）。"""
    text = '\n'.join([system, *memory.long_term, *memory.recent, f'用户问题: {question}'])
    return text[:budget]


def run_tests() -> None:
    """自动化断言测试：覆盖短期窗口、长期检索、预算裁剪、系统提示保护与边界用例。"""
    memory = Memory(window=2)
    memory.store_fact('用户偏好：喜欢简洁的回答')
    memory.store_fact('用户所在城市：长沙')
    memory.store_fact('用户关注：退款政策')

    # 1. 长期检索：问“退款”应找回退款相关的事实
    assert memory.recall('退款怎么办') == ['用户关注：退款政策']

    # 2. 去重：同一条事实只保存一次
    memory.store_fact('用户所在城市：长沙')
    assert len(memory.long_term) == 3

    # 3. 短期窗口：只保留最近 2 轮
    for turn in ['第一轮', '第二轮', '第三轮']:
        memory.remember_turn(turn)
    assert memory.recent == ['第二轮', '第三轮']

    # 4. 预算充足时全部装入，顺序为：记忆 -> 近期对话（从新到旧）
    system = '你是一个简洁的助手。'
    question = '退款怎么办'
    full = build_context(system, memory, question, budget=500)
    assert full.startswith(system) and full.endswith(f'用户问题: {question}')
    assert '用户关注：退款政策' in full and '第三轮' in full

    # 5. 预算紧张时，低优先级的近期对话先被丢弃，系统提示与问题一定保留
    tight_budget = estimate_tokens(system) + estimate_tokens(f'用户问题: {question}') + 12
    tight = build_context(system, memory, question, budget=tight_budget)
    assert system in tight and question in tight
    assert '第二轮' not in tight  # 最旧的对话被丢弃

    # 6. 直观版按末尾截断：预算很紧时会把问题截掉，结果不可控
    naive = build_context_naive(system, memory, question, budget=12)
    assert f'用户问题: {question}' not in naive

    # 7. 边界：预算连系统提示和问题都放不下时明确报错，而不是悄悄丢内容
    try:
        build_context(system, memory, question, budget=3)
    except ValueError:
        pass
    else:
        raise AssertionError('预算不足必须报错')

    print('✅ 记忆与上下文预算所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 记忆与上下文预算 {'*' * 12}", sep='', end='\n\n')
    memory = Memory(window=2)
    memory.store_fact('用户关注：退款政策')
    memory.store_fact('用户所在城市：长沙')
    for turn in ['用户: 你好', '助手: 你好，有什么可以帮你？']:
        memory.remember_turn(turn)
    print(build_context('你是一个简洁的助手。', memory, '退款怎么办', budget=80))
    run_tests()


if __name__ == '__main__':
    bootstrap()
