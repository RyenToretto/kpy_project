"""
[主题]: 多智能体通信协议：智能体名片 (AgentCard)、消息信封 (Envelope)、注册发现与按技能路由
[来源]: datawhalechina/hello-agents 第十章「智能体通信协议」(本文件为自行重写的标准库学习版，思想接近 Google A2A)
[难度]: Hard
[前置知识]: 06_mcp_beginners (JSON-RPC 与工具调用)、dataclass、json 序列化、Callable

一、主题说明
多个智能体要协作，必须先回答三个问题：
1. 谁能做什么？ -> 智能体名片 (AgentCard) 声明名字与技能，类似“简历”；
2. 消息长什么样？ -> 消息信封 (Envelope) 统一携带 id、发送方、接收方、类型、关联 id 与负载；
3. 怎么找到能干活的人？ -> 注册中心 (Registry) 按技能发现智能体，而不是硬编码名字。
与 MCP 的区别：MCP 解决“模型如何调用工具”，智能体协议解决“智能体之间如何互相委派任务”。

二、解法对比（以「调度器把任务交给能做它的智能体」为例）
1. 直观版 hardcode_dispatch: 在调度器里写死 if 任务类型 == 'math': calculator(...)，新增智能体要改调度代码。
   - 时间复杂度 O(1) 每次分派，但扩展性差，智能体之间强耦合。
2. 进阶版 MessageBus: 智能体注册名片与处理函数，消息按 receiver 或 skill 找到目标，统一返回结果信封。
   - 时间复杂度 O(智能体数) 按技能查找（可用字典索引降到 O(1)），新增智能体只需注册，调度器不变。

三、真实用途
- 大数据: 数据管道中各作业（抽取、清洗、建模）通过消息队列解耦，本质也是信封 + 路由。
- 数据分析: 报表智能体、取数智能体、可视化智能体按技能协作，避免一个大 Prompt 包揽所有事。
- AI Agent: A2A、AutoGen、CrewAI 的消息总线都是这套模型，理解它便于阅读任何多智能体代码。
- 全栈开发: 微服务之间的请求信封（traceId、来源、重试次数）与服务注册发现，思想完全相同。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from itertools import count

VALID_TYPES = {'task', 'result', 'error'}
_ids = count(1)  # 全局递增 id，保证每条消息可以被关联


@dataclass
class AgentCard:
    """智能体名片：名字、版本与可处理的技能列表。"""

    name: str
    skills: list[str]
    version: str = '1.0'


@dataclass
class Envelope:
    """消息信封：统一的消息外壳，负载 payload 由具体技能自定义。"""

    sender: str
    receiver: str
    type: str  # task / result / error
    payload: dict = field(default_factory=dict)
    msg_id: int = field(default_factory=lambda: next(_ids))
    reply_to: int | None = None  # 回复时指向原消息 id，用于关联请求与响应

    def to_json(self) -> str:
        """序列化为 JSON 字符串，便于跨进程或跨网络传输。"""
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def from_json(text: str) -> Envelope:
        """从 JSON 还原信封，并校验必填字段与消息类型。"""
        data = json.loads(text)
        for key in ('sender', 'receiver', 'type'):
            if key not in data:
                raise ValueError(f'信封缺少字段: {key}')
        if data['type'] not in VALID_TYPES:
            raise ValueError(f'非法消息类型: {data["type"]}')
        return Envelope(**data)


Handler = Callable[[dict], dict]


class MessageBus:
    """消息总线：注册智能体，按名字或技能路由消息，并把异常统一转成 error 信封。"""

    def __init__(self) -> None:
        self.cards: dict[str, AgentCard] = {}
        self.handlers: dict[str, Handler] = {}

    def register(self, card: AgentCard, handler: Handler) -> None:
        """注册智能体：名字不可重复，避免两个智能体互相覆盖。"""
        if card.name in self.cards:
            raise ValueError(f'智能体已存在: {card.name}')
        self.cards[card.name] = card
        self.handlers[card.name] = handler

    def discover(self, skill: str) -> list[str]:
        """按技能发现智能体，返回所有能处理该技能的名字（按注册顺序）。"""
        return [name for name, card in self.cards.items() if skill in card.skills]

    def send(self, message: Envelope) -> Envelope:
        """发送消息：找到接收方处理，返回 result 或 error 信封（不会把异常抛给调用方）。"""
        if message.type != 'task':
            return self._error(message, 'bad_type', '总线只接收 task 类型的消息')
        if message.receiver not in self.handlers:
            return self._error(message, 'unknown_receiver', f'找不到智能体: {message.receiver}')
        try:
            result_payload = self.handlers[message.receiver](message.payload)
        except Exception as exc:  # 智能体内部错误不能让整条流程崩溃，要转成信封返回
            return self._error(message, 'handler_error', str(exc))
        return Envelope(sender=message.receiver, receiver=message.sender, type='result',
                        payload=result_payload, reply_to=message.msg_id)

    def delegate(self, sender: str, skill: str, payload: dict) -> Envelope:
        """按技能委派任务：取第一个能处理该技能的智能体；没有人能做时返回 error。"""
        candidates = self.discover(skill)
        if not candidates:
            probe = Envelope(sender=sender, receiver='<none>', type='task', payload=payload)
            return self._error(probe, 'no_skill', f'没有智能体具备技能: {skill}')
        return self.send(Envelope(sender=sender, receiver=candidates[0], type='task', payload=payload))

    @staticmethod
    def _error(message: Envelope, code: str, detail: str) -> Envelope:
        """统一构造错误信封，并把错误码与原因放进 payload。"""
        return Envelope(sender=message.receiver, receiver=message.sender, type='error',
                        payload={'code': code, 'detail': detail}, reply_to=message.msg_id)


def hardcode_dispatch(task_type: str, payload: dict) -> dict:
    """直观版：调度器写死每种任务由谁处理（反面教材，新增智能体要改这里）。"""
    if task_type == 'math':
        return {'answer': payload['a'] + payload['b']}
    if task_type == 'upper':
        return {'answer': payload['text'].upper()}
    raise ValueError(f'不支持的任务: {task_type}')


def build_bus() -> MessageBus:
    """组装示例：一个数学智能体，一个文本智能体（同时具备 echo 技能）。"""
    bus = MessageBus()
    bus.register(AgentCard(name='calc', skills=['math']),
                 lambda p: {'answer': p['a'] + p['b']})
    bus.register(AgentCard(name='text', skills=['upper', 'echo']),
                 lambda p: {'answer': p['text'].upper()} if 'text' in p else {'answer': p})
    return bus


def run_tests() -> None:
    """自动化断言测试：覆盖名片发现、信封序列化、委派结果、错误信封与边界用例。"""
    bus = build_bus()

    # 1. 按技能发现：upper 只有 text 智能体具备
    assert bus.discover('upper') == ['text']
    assert bus.discover('nothing') == []

    # 2. 委派成功：结果信封的 type 为 result，并通过 reply_to 关联原请求
    request = Envelope(sender='boss', receiver='calc', type='task', payload={'a': 3, 'b': 4})
    reply = bus.send(request)
    assert reply.type == 'result' and reply.payload == {'answer': 7}
    assert reply.reply_to == request.msg_id and reply.receiver == 'boss'

    # 3. 按技能委派：不指定名字，由总线找到 text 智能体
    reply = bus.delegate('boss', 'upper', {'text': 'hello'})
    assert reply.type == 'result' and reply.payload == {'answer': 'HELLO'}

    # 4. 信封序列化往返：to_json 再 from_json 应得到等价的消息
    restored = Envelope.from_json(request.to_json())
    assert restored == request

    # 5. 错误信封：未注册的接收方、没人会的技能、智能体内部异常都不会抛出，而是返回 error
    missing = bus.send(Envelope(sender='boss', receiver='ghost', type='task'))
    assert missing.type == 'error' and missing.payload['code'] == 'unknown_receiver'

    no_skill = bus.delegate('boss', 'translate', {})
    assert no_skill.type == 'error' and no_skill.payload['code'] == 'no_skill'

    bus.register(AgentCard(name='broken', skills=['boom']), lambda p: 1 / 0)
    crashed = bus.delegate('boss', 'boom', {})
    assert crashed.type == 'error' and crashed.payload['code'] == 'handler_error'

    # 6. 非 task 类型的消息不能直接投递给总线
    wrong = bus.send(Envelope(sender='boss', receiver='calc', type='result'))
    assert wrong.payload['code'] == 'bad_type'

    # 7. 协议校验：缺字段或类型非法的 JSON 必须被拒绝
    try:
        Envelope.from_json('{"sender": "a", "type": "task"}')
    except ValueError:
        pass
    else:
        raise AssertionError('缺少 receiver 必须报错')
    try:
        Envelope.from_json('{"sender": "a", "receiver": "b", "type": "shout"}')
    except ValueError:
        pass
    else:
        raise AssertionError('非法 type 必须报错')

    # 8. 重复注册同名智能体必须报错
    try:
        bus.register(AgentCard(name='calc', skills=['math']), lambda p: p)
    except ValueError:
        pass
    else:
        raise AssertionError('重复注册必须报错')

    # 9. 直观版调度与总线结果一致（对照实验）
    assert hardcode_dispatch('math', {'a': 3, 'b': 4}) == {'answer': 7}

    print('✅ 智能体通信协议所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 多智能体通信协议 {'*' * 12}", sep='', end='\n\n')
    bus = build_bus()
    reply = bus.delegate('boss', 'math', {'a': 10, 'b': 32})
    print('数学任务回复:', reply.to_json())
    reply = bus.delegate('boss', 'translate', {})
    print('未知技能回复:', reply.to_json())
    run_tests()


if __name__ == '__main__':
    bootstrap()
