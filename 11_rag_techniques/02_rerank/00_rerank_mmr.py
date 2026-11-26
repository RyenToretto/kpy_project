"""
[主题]: 两阶段检索的重排 (Rerank) 与最大边际相关 MMR (Maximal Marginal Relevance) 去冗余
[来源]: NirDiamant/RAG_Techniques 「Reranking」章节思路 (本文件为自行重写的标准库学习版)
[难度]: Hard
[前置知识]: 11_rag_techniques/01_query_transform (相似度与排名)、列表推导式、贪心算法

一、主题说明
RAG 通常分两步：
1. 粗召回（第一阶段）: 用便宜的方法（向量或关键词）快速从海量文档里选出 Top-N 候选；
2. 精排（重排 Rerank）: 用更精细、更贵的打分方式，对 N 个候选重新排序，选出最终 Top-K。
重排的常见问题是“候选都很像”：前几名可能是同一段话的重复版本，给大模型的上下文就浪费了。
MMR 在相关性与多样性之间权衡，每次选择一个“与问题相关，且与已选内容不重复”的文档：
score = λ · relevance(文档, 问题) - (1 - λ) · max_similarity(文档, 已选文档)

二、解法对比（以「从候选中选出 K 个给模型」为例）
1. 直观版 top_k_by_relevance: 直接按相关性取前 K 个，可能全是重复内容。
   - 时间复杂度 O(N log N)，空间复杂度 O(N)
2. 进阶版 mmr_select: 贪心地逐个选择，每一步兼顾相关性与和已选内容的差异。
   - 时间复杂度 O(K · N)（每步要与已选内容比较），空间复杂度 O(N)

三、真实用途
- 大数据: 大规模检索系统里，精排和去重决定了最终喂给模型的信息密度。
- 数据分析: 从大量报告中选代表性段落做摘要时，MMR 能避免重复。
- AI Agent / RAG: 上下文窗口有限，多样性直接等于信息量；这是提升回答质量的关键步骤。
- 全栈开发: 搜索结果页的“去重 + 多样化展示”，也是同一套思想。
"""

from __future__ import annotations

from collections import Counter


def bigrams(text: str) -> Counter[str]:
    """字符二元组袋：比单字更能反映词语搭配，适合做精排的打分特征。"""
    chars = [ch for ch in text if not ch.isspace()]
    return Counter(a + b for a, b in zip(chars, chars[1:]))


def overlap_score(query: str, doc: str) -> float:
    """精排打分（示意）：问题的二元组有多少在文档中出现，按问题二元组总数归一化。"""
    q_grams = bigrams(query)
    d_grams = bigrams(doc)
    total = sum(q_grams.values())
    if total == 0:
        return 0.0
    hit = sum(min(count, d_grams[gram]) for gram, count in q_grams.items())
    return hit / total


def similarity(a: str, b: str) -> float:
    """两段文本的相似度（二元组 Jaccard），用于衡量“内容是否重复”。"""
    grams_a, grams_b = set(bigrams(a)), set(bigrams(b))
    if not grams_a or not grams_b:
        return 0.0
    return len(grams_a & grams_b) / len(grams_a | grams_b)


def top_k_by_relevance(query: str, candidates: list[str], k: int) -> list[str]:
    """直观版：只看相关性，取分数最高的 K 个。"""
    ranked = sorted(candidates, key=lambda doc: (-overlap_score(query, doc), doc))
    return ranked[:k]


def mmr_select(query: str, candidates: list[str], k: int, lambda_: float = 0.7) -> list[str]:
    """MMR 贪心选择：每一步选出 λ·相关性 - (1-λ)·与已选最大相似度 最高的候选。"""
    selected: list[str] = []
    remaining = list(candidates)
    while remaining and len(selected) < k:
        def mmr_value(doc: str) -> float:
            relevance = overlap_score(query, doc)
            redundancy = max((similarity(doc, chosen) for chosen in selected), default=0.0)
            return lambda_ * relevance - (1 - lambda_) * redundancy

        best = max(remaining, key=lambda doc: (mmr_value(doc), doc))
        selected.append(best)
        remaining.remove(best)
    return selected


CANDIDATES = [
    '商品签收后七天内可以申请退款，退款原路返回。',
    '商品签收后七天内可以申请退款，退款原路返回。',  # 与上一条完全重复
    '退款申请提交后三个工作日内处理完成。',
    '会员每月可以享受两次免运费服务。',
]


def run_tests() -> None:
    """自动化断言测试：覆盖相关性、重复惩罚、多样性与边界用例。"""
    query = '怎么申请退款'

    # 1. 直观版：只看相关性，前两名可能是重复的同一段
    naive = top_k_by_relevance(query, CANDIDATES, k=2)
    assert naive[0] == naive[1] == CANDIDATES[0]

    # 2. MMR：第二个结果必须与第一个不同，避免重复占用上下文
    diverse = mmr_select(query, CANDIDATES, k=2)
    assert diverse[0] == CANDIDATES[0]
    assert diverse[1] != diverse[0]

    # 3. 相关性最高的文档仍然排第一（MMR 不会丢掉最相关的内容）
    assert diverse[0] == top_k_by_relevance(query, CANDIDATES, k=1)[0]

    # 4. 边界：K 大于候选数量时，返回全部候选且不重复
    everything = mmr_select(query, CANDIDATES, k=10)
    assert len(everything) == len(CANDIDATES)

    # 5. 相似度性质：同一段文本相似度为 1，完全无关为 0
    assert similarity('退款流程', '退款流程') == 1.0
    assert similarity('退款流程', 'zzzz') == 0.0

    # 6. 边界：没有候选时返回空列表；问题为空时相关性为 0
    assert mmr_select(query, [], k=3) == []
    assert overlap_score('', '退款') == 0.0

    print('✅ 重排与 MMR 多样性所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 重排与 MMR 去冗余 {'*' * 12}", sep='', end='\n\n')
    query = '怎么申请退款'
    print('只看相关性 Top-2:')
    for doc in top_k_by_relevance(query, CANDIDATES, k=2):
        print(f'  - {doc}')
    print('MMR Top-2（去重后）:')
    for doc in mmr_select(query, CANDIDATES, k=2):
        print(f'  - {doc}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
