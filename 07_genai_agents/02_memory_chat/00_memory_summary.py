"""
[主题]: 带记忆的对话 Agent (滑动窗口记忆 + 摘要压缩 + 关键词回忆)
[来源]: NirDiamant/GenAI_Agents 「记忆类 Agent」案例思路 (本文件为自行重写的标准库学习版，不需要 API Key)
[难度]: Medium
[前置知识]: 07_genai_agents/00_single_agent (工具调用)、dataclass、列表切片、集合

一、主题说明
大模型本身没有长期记忆，每次调用只能看到你放进去的上下文。常见做法是三层记忆：
1. 短期记忆: 最近 N 轮原文，保证当前对话连贯；
2. 长期摘要: 更早的对话压缩成几句话，控制 Token 成本；
3. 回忆检索: 需要时按关键词从历史里找回相关内容。
本文件用规则版“摘要器”代替大模型摘要，离线即可运行，但保留了完整的记忆流程。

二、解法对比（以「保留多少历史」为例）
1. 直观版 keep_all: 把全部历史都塞进上下文。
   - 时间复杂度 O(总轮数)，Token 随对话无限增长，很快超出上限。
2. 进阶版 ConversationMemory: 短期窗口保留原文，超出部分压缩进摘要。
   - 时间复杂度 O(窗口大小)（每轮），空间复杂度 O(窗口大小 + 摘要长度)

三、真实用途
- 大数据: 长对话日志的压缩与归档，同样是“近期原文 + 历史摘要”。
- 数据分析: 客服、销售对话的要点提取，可以直接复用摘要与关键词检索的思路。
- AI Agent / RAG: 这是 Agent 记忆模块的标准骨架，后续可把摘要器替换为真实大模型。
- 全栈开发: 聊天产品的“历史消息分页 + 上下文截断”，本质是同一套设计。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Turn:
    """一轮对话：用户说了什么、助手回了什么。"""

    user: str
    assistant: str


def summarize_turns(turns: list[Turn], max_chars: int = 60) -> str:
    """规则版摘要：把每轮的用户问题拼在一起，超出长度就截断。真实场景应交给大模型生成摘要。"""
    if not turns:
        return ''
    questions = '；'.join(turn.user for turn in turns)
    return questions if len(questions) <= max_chars else questions[:max_chars] + '…'


@dataclass
class ConversationMemory:
    """三层记忆：摘要（更早）+ 近期原文（窗口内）+ 关键词回忆（全部历史）。"""

    window_size: int = 2  # 短期记忆保留的最近轮数
    summary: str = ''  # 长期摘要
    recent: list[Turn] = field(default_factory=list)
    archive: list[Turn] = field(default_factory=list)  # 完整历史，用于关键词回忆

    def add(self, user: str, assistant: str) -> None:
        """记录新一轮；超出窗口的旧轮次被压缩进摘要。"""
        turn = Turn(user, assistant)
        self.archive.append(turn)
        self.recent.append(turn)
        if len(self.recent) > self.window_size:
            overflow = self.recent[:-self.window_size]  # 需要压缩的旧轮次
            self.recent = self.recent[-self.window_size:]
            # 新摘要 = 旧摘要 + 刚被挤出窗口的内容，再统一压缩
            merged = [Turn('（历史摘要）' + self.summary, '')] if self.summary else []
            self.summary = summarize_turns(merged + overflow)

    def build_context(self, question: str) -> str:
        """拼装发给模型的上下文：摘要 + 近期原文 + 与当前问题相关的历史片段。"""
        parts: list[str] = []
        if self.summary:
            parts.append(f'[长期摘要] {self.summary}')
        for turn in self.recent:
            parts.append(f'用户: {turn.user}\n助手: {turn.assistant}')
        recalled = self.recall(question)
        if recalled:
            parts.append('[相关回忆] ' + ' | '.join(f'{t.user}->{t.assistant}' for t in recalled))
        parts.append(f'当前问题: {question}')
        return '\n'.join(parts)

    def recall(self, query: str, top_k: int = 1) -> list[Turn]:
        """关键词回忆：统计问题与历史轮次的共同字符数，返回重叠最多的前 top_k 轮（忽略近期窗口内的轮次）。"""
        recent_set = set(id(turn) for turn in self.recent)
        query_chars = set(query)
        scored: list[tuple[int, int, Turn]] = []
        for index, turn in enumerate(self.archive):
            if id(turn) in recent_set:  # 近期原文已经在上下文里，不重复回忆
                continue
            overlap = len(query_chars & set(turn.user))
            if overlap > 0:
                scored.append((overlap, -index, turn))  # 同分时优先更早的记录的相反顺序，保证稳定
        scored.sort(reverse=True)
        return [turn for _, _, turn in scored[:top_k]]


def run_tests() -> None:
    """自动化断言测试：覆盖窗口滚动、摘要压缩、回忆与边界用例。"""
    memory = ConversationMemory(window_size=2)

    # 1. 窗口内的对话保留原文，没有摘要
    memory.add('怎么退款', '签收后七天内可以申请')
    memory.add('会员有什么权益', '每月两张优惠券')
    assert len(memory.recent) == 2 and memory.summary == ''

    # 2. 超出窗口：最早的一轮被压缩进摘要，近期窗口仍是 2 轮
    memory.add('物流多久到', '一般三天内')
    assert len(memory.recent) == 2
    assert memory.recent[0].user == '会员有什么权益'
    assert '怎么退款' in memory.summary  # 旧问题进入摘要

    # 3. 完整历史始终保存在 archive 中
    assert len(memory.archive) == 3

    # 4. 关键词回忆：问“退款”时应能找回“怎么退款”这一轮（它已不在窗口内）
    context = memory.build_context('退款规则是什么')
    assert '[长期摘要]' in context
    assert '相关回忆' in context and '怎么退款' in context
    assert '当前问题: 退款规则是什么' in context

    # 5. 近期窗口内的轮次不会重复出现在“相关回忆”里
    recalled = memory.recall('会员有什么权益')  # 问题与近期轮次高度相似，但它不应被回忆出来
    assert all(turn not in memory.recent for turn in recalled)

    # 6. 摘要长度受限：超长问题会被截断
    long_text = '很长的问题' * 30
    assert len(summarize_turns([Turn(long_text, '')], max_chars=10)) == 11  # 10 个字符 + 省略号

    # 7. 边界：没有任何历史时，上下文只包含当前问题
    empty = ConversationMemory()
    assert empty.build_context('你好') == '当前问题: 你好'
    assert summarize_turns([]) == ''

    print('✅ 带记忆的对话 Agent 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 带记忆的对话 Agent {'*' * 12}", sep='', end='\n\n')
    memory = ConversationMemory(window_size=2)
    for user, assistant in [
        ('怎么退款', '签收后七天内可以申请'),
        ('会员有什么权益', '每月两张优惠券'),
        ('物流多久到', '一般三天内'),
    ]:
        memory.add(user, assistant)
    print('模型看到的上下文:')
    print(memory.build_context('退款规则是什么'))
    run_tests()


if __name__ == '__main__':
    bootstrap()
