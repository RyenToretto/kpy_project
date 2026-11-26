"""
[主题]: 行业案例一：客服工单自动分流 (意图识别 / 优先级 / 部门路由 / 模板回复 / 转人工)
[来源]: NirDiamant/GenAI_Agents 客服类 Agent 案例思路 (本文件为自行重写的标准库学习版，不需要 API Key)
[难度]: Medium
[前置知识]: 07_genai_agents/00_single_agent (工具调用)、dataclass、字典、列表

一、主题说明
电商、SaaS、教培等公司的客服每天要处理大量重复问题。自动分流的目标是：
- 先判断用户意图（退款、物流、投诉、其他）；
- 按意图与紧急程度分配优先级与负责部门；
- 能被模板直接回答的，自动回复；涉及投诉或情绪激烈的，转人工。
这里用关键词规则代替大模型分类，结构与真实项目一致，便于替换。

二、解法对比（以「判断一条消息属于哪个意图」为例）
1. 直观版 classify_if_chain: 写一长串 if/elif 逐个判断关键词。
   - 时间复杂度 O(规则数 * 文本长度)，规则多了难以维护。
2. 进阶版 classify: 规则表用数据结构保存（意图 -> 关键词列表），统一遍历匹配，新增意图只改数据。
   - 时间复杂度 O(规则关键词总数 * 文本长度)，空间复杂度 O(规则数)

三、真实用途
- 大数据: 工单与舆情文本的海量分类，先用规则快速过滤，再交给模型处理疑难样本。
- 数据分析: 工单按意图统计，就能看出哪类问题最多，指导产品改进。
- AI Agent / RAG: 客服 Agent 的第一步就是路由，错误的路由会让后续回答全部偏题。
- 全栈开发: 工单系统的自动分派、SLA 超时提醒，都是后端业务的常见需求。
"""

from __future__ import annotations

from dataclasses import dataclass

# 意图规则表：新增意图只需要在这里加一行，不必改动判断逻辑
INTENT_RULES: dict[str, list[str]] = {
    'refund': ['退款', '退货', '退钱'],
    'logistics': ['物流', '快递', '发货', '没到'],
    'complaint': ['投诉', '垃圾', '骗子', '太差'],
}

# 意图 -> (负责部门, 基础优先级，数字越小越紧急)
ROUTING: dict[str, tuple[str, int]] = {
    'refund': ('售后组', 2),
    'logistics': ('物流组', 3),
    'complaint': ('客诉组', 1),
    'other': ('通用客服', 4),
}

# 模板回复：能直接回答的意图给出固定话术，其余交给人工
TEMPLATE_REPLIES: dict[str, str] = {
    'refund': '您好，签收后七天内可以在订单页申请退款，我们会在三个工作日内原路返回。',
    'logistics': '您好，请在订单详情中查看最新物流信息，如超过承诺时效请告诉我们订单号。',
}


@dataclass(frozen=True)
class TriageResult:
    """分流结果：意图、负责部门、优先级、是否转人工以及自动回复内容。"""

    intent: str
    department: str
    priority: int
    need_human: bool
    auto_reply: str | None


def classify_if_chain(text: str) -> str:
    """直观版：用 if/elif 逐条判断，规则一多就很难读。注意投诉要排在最前面。"""
    if '投诉' in text or '垃圾' in text or '骗子' in text or '太差' in text:
        return 'complaint'
    elif '退款' in text or '退货' in text or '退钱' in text:
        return 'refund'
    elif '物流' in text or '快递' in text or '发货' in text or '没到' in text:
        return 'logistics'
    return 'other'


def classify(text: str) -> str:
    """进阶版：按优先级顺序遍历规则表，第一个命中的意图即为结果。投诉优先级最高，先检查。"""
    # 投诉的优先级最高，避免“退款一直没到，我要投诉”被误判为普通退款
    for intent in ['complaint', 'refund', 'logistics']:
        if any(keyword in text for keyword in INTENT_RULES[intent]):
            return intent
    return 'other'


def triage(text: str) -> TriageResult:
    """完整分流：识别意图 -> 查路由表 -> 决定是否自动回复或转人工。"""
    intent = classify(text)
    department, priority = ROUTING[intent]
    # 投诉和“other”一律转人工；有模板的意图自动回复
    need_human = intent in ('complaint', 'other')
    auto_reply = None if need_human else TEMPLATE_REPLIES.get(intent)
    return TriageResult(intent, department, priority, need_human, auto_reply)


def run_tests() -> None:
    """自动化断言测试：覆盖各类意图、优先级冲突与边界用例。"""
    # 1. 两种分类写法结果一致
    samples = ['我要退款', '快递没到', '你们是骗子', '请问营业时间', '退款一直没到，我要投诉']
    for text in samples:
        assert classify(text) == classify_if_chain(text), text

    # 2. 常规意图路由
    refund = triage('我要退款')
    assert refund.intent == 'refund' and refund.department == '售后组'
    assert refund.need_human is False and refund.auto_reply is not None

    logistics = triage('快递没到')
    assert logistics.department == '物流组' and logistics.auto_reply is not None

    # 3. 优先级冲突：同时提到退款与投诉时，应判为投诉并转人工
    mixed = triage('退款一直没到，我要投诉')
    assert mixed.intent == 'complaint' and mixed.need_human is True
    assert mixed.priority == 1 and mixed.auto_reply is None

    # 4. 未知问题：归入 other，转人工且没有自动回复
    other = triage('请问营业时间')
    assert other.intent == 'other' and other.need_human is True

    # 5. 边界：空文本归入 other，不会报错
    assert triage('').intent == 'other'

    print('✅ 客服工单分流所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 客服工单自动分流 {'*' * 12}", sep='', end='\n\n')
    tickets = ['我想申请退款', '快递三天没到', '你们的服务太差了，我要投诉', '请问有发票吗']
    for ticket in tickets:
        result = triage(ticket)
        print(f'工单: {ticket}')
        print(f'  意图={result.intent} 部门={result.department} 优先级={result.priority} 转人工={result.need_human}')
        print(f'  自动回复: {result.auto_reply or "（无，已转人工）"}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
