"""
[主题]: RAG 评估指标 (上下文召回 Context Recall / 答案忠实度 Faithfulness / 答案相关性 Answer Relevance)
[来源]: NirDiamant/RAG_Techniques 「Evaluation」章节思路 (本文件为自行重写的标准库学习版)
[难度]: Medium
[前置知识]: 04_all_in_rag/02_evaluation (Recall@K、MRR)、11_rag_techniques/02_rerank (二元组相似度)

一、主题说明
RAG 系统“好不好”要拆开看，至少三件事：
1. 上下文召回: 检索到的资料里，是否包含回答所需的事实（找没找到）；
2. 答案忠实度: 回答里的每一句话，是否都能在资料中找到依据（有没有胡编）；
3. 答案相关性: 回答是否真的在回应用户的问题（答没答题）。
真实项目里常用大模型当“裁判”打分（如 RAGAS 框架）。这里用字符二元组重叠作为离线代理指标，计算逻辑透明，便于理解。

二、解法对比（以「判断一句回答是否有依据」为例）
1. 直观版 faithful_exact: 要求回答句子在资料中逐字出现。
   - 时间复杂度 O(句子数 · 资料长度)，几乎任何改写都会被判为“无依据”，过于严格。
2. 进阶版 faithful_fuzzy: 计算回答句子与各段资料的二元组覆盖率，超过阈值即视为有依据。
   - 时间复杂度 O(句子数 · 资料数 · 长度)，允许合理改写，更接近真实判断。

三、真实用途
- 大数据: 评估一次检索策略改动是否真的变好，需要可重复、可量化的指标。
- 数据分析: 报表问答机器人上线前，用召回与忠实度指标确认它不会胡编数字。
- AI Agent / RAG: 评估是 RAG 迭代的“仪表盘”，没有指标就无法判断改动是否有效。
- 全栈开发: 线上监控里的“回答有依据率”“检索命中率”，就是这些指标的生产版本。
"""

from __future__ import annotations

from collections import Counter


def bigrams(text: str) -> Counter[str]:
    """字符二元组袋：去掉空白与标点后，相邻两个字符组成一个二元组。"""
    chars = [ch for ch in text if ch.strip() and ch not in '，。！？；：、']
    return Counter(a + b for a, b in zip(chars, chars[1:]))


def coverage(claim: str, evidence: str) -> float:
    """claim 的二元组中，有多少比例出现在 evidence 中（0~1）。"""
    claim_grams = bigrams(claim)
    evidence_grams = bigrams(evidence)
    total = sum(claim_grams.values())
    if total == 0:
        return 0.0
    hit = sum(min(count, evidence_grams[gram]) for gram, count in claim_grams.items())
    return hit / total


def context_recall(reference_facts: list[str], contexts: list[str], threshold: float = 0.8) -> float:
    """上下文召回：标准答案中的每条事实，能被检索上下文覆盖（超过阈值）的比例。"""
    if not reference_facts:
        return 1.0
    found = sum(1 for fact in reference_facts if any(coverage(fact, ctx) >= threshold for ctx in contexts))
    return found / len(reference_facts)


def faithful_exact(answer_sentences: list[str], contexts: list[str]) -> float:
    """直观版忠实度：回答句子必须在某段资料中逐字出现，否则不算有依据。"""
    supported = sum(1 for sentence in answer_sentences if any(sentence in ctx for ctx in contexts))
    return supported / len(answer_sentences) if answer_sentences else 1.0


def faithful_fuzzy(answer_sentences: list[str], contexts: list[str], threshold: float = 0.6) -> float:
    """进阶版忠实度：允许改写，只要二元组覆盖率超过阈值即视为有依据。"""
    supported = sum(1 for s in answer_sentences if any(coverage(s, ctx) >= threshold for ctx in contexts))
    return supported / len(answer_sentences) if answer_sentences else 1.0


def answer_relevance(question: str, answer: str) -> float:
    """答案相关性：问题的二元组有多少出现在回答中，衡量“有没有回应问题”。"""
    return coverage(question, answer)


CONTEXTS = [
    '商品签收后七天内可以申请退款，退款原路返回。',
    '会员每月可以享受两次免运费服务。',
]


def run_tests() -> None:
    """自动化断言测试：覆盖召回、精确与模糊忠实度、相关性与边界用例。"""
    # 1. 召回：标准答案的事实都能在上下文中找到 -> 召回率 1.0
    facts = ['签收后七天内可以申请退款']
    assert context_recall(facts, CONTEXTS) == 1.0

    # 2. 召回：找不到的事实不计入 -> 召回率 0.0
    assert context_recall(['火星可以免费寄快递'], CONTEXTS) == 0.0

    # 3. 精确忠实度太严格：改写后的句子会被判为无依据
    rewritten = ['签收后七天内能申请退款']  # 只改了一个字，逐字匹配失败
    assert faithful_exact(rewritten, CONTEXTS) == 0.0

    # 4. 模糊忠实度允许改写：同一句改写后仍被判为有依据
    assert faithful_fuzzy(rewritten, CONTEXTS) == 1.0

    # 5. 胡编的内容（与资料无关）应该被识别出来
    hallucinated = ['我们支持免费上门安装服务']
    assert faithful_fuzzy(hallucinated, CONTEXTS) == 0.0

    # 6. 相关性：回答回应了问题 -> 分数高；答非所问 -> 分数低
    question = '怎么申请退款'
    relevant = answer_relevance(question, '您可以在签收后七天内申请退款')
    off_topic = answer_relevance(question, '今天天气很好')
    assert relevant > 0.5 and off_topic < relevant

    # 7. 边界：空回答的忠实度按约定为 1.0（没有需要验证的句子），空事实的召回为 1.0
    assert faithful_fuzzy([], CONTEXTS) == 1.0
    assert context_recall([], CONTEXTS) == 1.0

    print('✅ RAG 评估指标所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} RAG 评估指标 {'*' * 12}", sep='', end='\n\n')
    question = '怎么申请退款'
    answer = '您可以在签收后七天内申请退款，退款原路返回。'
    print(f'问题: {question}')
    print(f'回答: {answer}')
    print(f'上下文召回: {context_recall(["签收后七天内可以申请退款"], CONTEXTS):.2f}')
    print(f'忠实度（精确）: {faithful_exact([answer], CONTEXTS):.2f}')
    print(f'忠实度（模糊）: {faithful_fuzzy([answer], CONTEXTS):.2f}')
    print(f'答案相关性: {answer_relevance(question, answer):.2f}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
