"""
[主题]: 行业案例二：研报 / 新闻要点提炼 (时间排序 / 正负面信号打分 / 结构化提纲输出)
[来源]: NirDiamant/GenAI_Agents 研究与报告类 Agent 案例思路 (本文件为自行重写的标准库学习版，不需要 API Key)
[难度]: Medium
[前置知识]: 03_industry_cases/00_customer_service_triage (规则与分类)、dataclass、sorted 排序、字典

一、主题说明
分析师每天要读大量新闻与公告。研报 Agent 的常见流程是：
1. 收集: 按主题收集多条资料（这里用内置数据代替网络检索）；
2. 排序: 按日期整理成时间线，最新的信息更重要；
3. 打分: 统计正面与风险词，给出简单的情绪倾向；
4. 输出: 生成固定结构的提纲，方便人工复核，而不是直接输出一段不可控的长文。
用关键词计数代替大模型情绪分析，结构和流程与真实项目一致。

二、解法对比（以「判断一篇资料的情绪倾向」为例）
1. 直观版 sentiment_naive: 只看有没有正面词，一句话同时含正负面时会偏向正面。
   - 时间复杂度 O(文本长度 * 词数)
2. 进阶版 sentiment_score: 正面词计数 - 风险词计数，结果为正/负/中性三态。
   - 时间复杂度 O(文本长度 * 词数)，空间复杂度 O(1)

三、真实用途
- 大数据: 舆情监控大盘按天汇总正负面声量，就是这套打分思路的扩大版。
- 数据分析: 用户评论的情绪趋势，同样可以用计数打分快速得到第一版结论。
- AI Agent / RAG: 研究类 Agent 的“资料整理 -> 结构化输出”是通用模板，报告质量取决于提纲是否稳定。
- 全栈开发: 内容平台的自动摘要与标签，后端可以先用规则完成，再接入模型。
"""

from __future__ import annotations

from dataclasses import dataclass

POSITIVE_WORDS = ['增长', '盈利', '突破', '扩张', '领先']
RISK_WORDS = ['下滑', '亏损', '诉讼', '违约', '裁员']


@dataclass(frozen=True)
class NewsItem:
    """一条资料：日期（YYYY-MM-DD）、标题与正文。"""

    date: str
    title: str
    body: str


def sentiment_naive(body: str) -> str:
    """直观版：只要出现正面词就判为正面，一句话里同时有风险词也会被忽略。"""
    return '正面' if any(word in body for word in POSITIVE_WORDS) else '中性'


def sentiment_score(body: str) -> tuple[str, int]:
    """进阶版：正面词次数减去风险词次数，得分 > 0 为正面，< 0 为风险，= 0 为中性。"""
    positive = sum(body.count(word) for word in POSITIVE_WORDS)
    risk = sum(body.count(word) for word in RISK_WORDS)
    score = positive - risk
    if score > 0:
        return '正面', score
    if score < 0:
        return '风险', score
    return '中性', 0


def build_outline(topic: str, items: list[NewsItem]) -> str:
    """生成固定结构的提纲：按日期升序列出时间线，再汇总正负面要点。"""
    timeline = sorted(items, key=lambda item: item.date)  # 按日期从早到晚排列
    lines = [f'# {topic} 研究提纲', '', '## 一、时间线']
    for item in timeline:
        label, score = sentiment_score(item.body)
        lines.append(f'- {item.date} [{label} {score:+d}] {item.title}')

    positives = [item.title for item in timeline if sentiment_score(item.body)[0] == '正面']
    risks = [item.title for item in timeline if sentiment_score(item.body)[0] == '风险']
    # 注意：先算出列表再决定是否用“暂无”占位，避免运算符优先级造成的误判
    positive_lines = [f'- {title}' for title in positives] or ['- 暂无']
    risk_lines = [f'- {title}' for title in risks] or ['- 暂无']
    lines += ['', '## 二、正面信号', *positive_lines]
    lines += ['', '## 三、风险提示', *risk_lines]

    if len(risks) > len(positives):
        conclusion = '风险信号多于正面信号，建议保守看待，继续跟踪。'
    elif len(positives) > len(risks):
        conclusion = '正面信号多于风险信号，可以重点关注，但仍需核实来源。'
    else:
        conclusion = '正负信号持平，需要更多资料再判断。'
    lines += ['', '## 四、结论（需人工复核）', conclusion]
    return '\n'.join(lines)


SAMPLE_ITEMS = [
    NewsItem('2026-03-02', '新品发布会召开', '公司新品推动营收增长，市场份额持续领先。'),
    NewsItem('2026-01-15', '季度财报发布', '本季度盈利同比增长，海外业务明显扩张。'),
    NewsItem('2026-02-20', '供应链调整公告', '原材料成本上涨，部分产线产能下滑。'),
]


def run_tests() -> None:
    """自动化断言测试：覆盖情绪打分、混合句子、提纲结构与边界用例。"""
    # 1. 混合句子：直观版只看正面词，打分版会扣掉风险词
    mixed = '营收增长，但诉讼增加，产能下滑'
    assert sentiment_naive(mixed) == '正面'
    assert sentiment_score(mixed) == ('风险', -1)  # 正面 1 次 - 风险 2 次 = -1

    # 2. 纯正面与中性
    assert sentiment_score('盈利突破，领先同行') == ('正面', 3)
    assert sentiment_score('今天天气不错') == ('中性', 0)

    # 3. 提纲：时间线按日期升序，三个章节都存在
    outline = build_outline('某科技公司', SAMPLE_ITEMS)
    lines = outline.split('\n')
    dated = [line for line in lines if line.startswith('- 2026')]
    assert [line[2:12] for line in dated] == ['2026-01-15', '2026-02-20', '2026-03-02']
    assert '## 二、正面信号' in outline and '## 三、风险提示' in outline
    assert '供应链调整公告' in outline.split('## 三、风险提示')[1]

    # 4. 结论依据正负信号数量判断
    assert '正面信号多于风险信号' in outline

    # 5. 边界：没有任何资料时，正面与风险都显示“暂无”，结论为持平
    empty = build_outline('空主题', [])
    assert empty.count('- 暂无') == 2
    assert '持平' in empty

    print('✅ 研报要点提炼所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 研报要点提炼 {'*' * 12}", sep='', end='\n\n')
    print(build_outline('某科技公司', SAMPLE_ITEMS))
    run_tests()


if __name__ == '__main__':
    bootstrap()
