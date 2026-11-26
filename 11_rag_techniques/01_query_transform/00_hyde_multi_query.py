"""
[主题]: 查询改写 (HyDE 假设性文档 / 多查询扩展 Multi-Query / RRF 排名融合)
[来源]: NirDiamant/RAG_Techniques 「Query Transformations」章节思路 (本文件为自行重写的标准库学习版)
[难度]: Medium
[前置知识]: 11_rag_techniques/00_chunking (切块)、Counter、排序与字典

一、主题说明
用户的问题通常很短、措辞口语化，而文档写得正式、细致，两者的词汇经常对不上（“怎么退钱”与“申请退款”）。查询改写就是让“问题”更像“文档”：
- HyDE (Hypothetical Document Embeddings): 先让模型写一段“假设的答案”，再用这段话去检索。答案的措辞更接近真实文档。
- Multi-Query: 把一个问题改写成多个不同说法，分别检索，减少只靠一种措辞的漏召回。
- RRF (Reciprocal Rank Fusion): 把多次检索的排名融合成一个排名，公式 score = Σ 1/(k + rank)，不需要调各路得分的尺度。
这里用字符袋相似度代替向量，用规则表代替大模型生成，结构与真实系统一致。

二、解法对比（以「把原始问题拿去检索」为例）
1. 直观版 retrieve_raw: 直接用用户原话检索一次。
   - 时间复杂度 O(文档数 * 词表)，原话与文档措辞不一致时容易漏召回。
2. 进阶版 hyde_retrieve / multi_query_retrieve: 先改写再检索，多路结果用 RRF 融合。
   - 时间复杂度 O(改写数 * 文档数 * 词表)，召回率更高，但成本随改写数线性增长。

三、真实用途
- 大数据: 海量知识库中，改写能显著提升冷门问题的召回，减少“查不到”的情况。
- 数据分析: 业务人员用口语提问，改写后能命中规范的指标定义文档。
- AI Agent / RAG: 这是 RAG 最常用的“召回增强”手段，成本低、效果直观。
- 全栈开发: 搜索框的同义词扩展、纠错、多关键词召回，本质都是查询改写。
"""

from __future__ import annotations

from collections import Counter

DOCS = {
    'refund': '商品签收后七天内可以在订单页申请退款，退款原路返回。',
    'member': '会员每月可以享受两次免运费服务，会员等级每季度评定一次。',
    'logistics': '订单发货后可以在物流页面查看快递轨迹，一般三天内送达。',
}

# HyDE 的“假设答案”表：真实系统中这里是大模型根据问题生成的一段文字
HYPOTHETICAL_ANSWERS = {
    '钱怎么退回来': '商品签收后可以在订单页申请退款，退款原路返回。',
}

# 多查询的改写表：真实系统中这里是大模型生成的几种问法
PARAPHRASES = {
    '怎么退钱': ['怎么退钱', '如何申请退款', '退款流程是什么'],
}


def char_vector(text: str) -> Counter[str]:
    """字符袋向量：去掉标点与空白后的字符频次，用于计算相似度。"""
    return Counter(ch for ch in text if ch.strip() and ch not in '，。！？')


def cosine(a: Counter[str], b: Counter[str]) -> float:
    """余弦相似度。"""
    dot = sum(a[k] * b[k] for k in a.keys() & b.keys())
    norm_a = sum(v * v for v in a.values()) ** 0.5
    norm_b = sum(v * v for v in b.values()) ** 0.5
    return 0.0 if norm_a == 0 or norm_b == 0 else dot / (norm_a * norm_b)


def rank_docs(query: str) -> list[str]:
    """用查询向量对所有文档打分，返回文档 ID 按相似度从高到低的排序。"""
    query_vec = char_vector(query)
    scored = sorted(DOCS, key=lambda doc_id: (-cosine(query_vec, char_vector(DOCS[doc_id])), doc_id))
    return scored


def retrieve_raw(question: str, top_k: int = 1) -> list[str]:
    """直观版：直接拿用户原话检索。"""
    return rank_docs(question)[:top_k]


def hyde_retrieve(question: str, top_k: int = 1) -> list[str]:
    """HyDE：用“假设答案”代替原问题去检索；没有假设答案时回退为原问题。"""
    hypothetical = HYPOTHETICAL_ANSWERS.get(question, question)
    return rank_docs(hypothetical)[:top_k]


def rrf_fuse(rankings: list[list[str]], k: int = 60) -> list[str]:
    """RRF 融合：每个文档在每路排名中得到 1/(k+rank) 分，累加后降序排列。"""
    scores: Counter[str] = Counter()
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):  # 排名从 1 开始
            scores[doc_id] += 1.0 / (k + rank)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))]


def multi_query_retrieve(question: str, top_k: int = 1) -> list[str]:
    """Multi-Query：对每个改写分别检索，再用 RRF 融合；没有改写表时只检索原问题。"""
    variants = PARAPHRASES.get(question, [question])
    rankings = [rank_docs(variant) for variant in variants]
    return rrf_fuse(rankings)[:top_k]


def run_tests() -> None:
    """自动化断言测试：覆盖原问题、HyDE、多查询、RRF 数学性质与边界用例。"""
    # 1. 返回结果的数量受 top_k 控制
    assert len(retrieve_raw('退款', top_k=2)) == 2

    # 2. HyDE：用“假设答案”检索，应该稳定命中退款文档（原问题的措辞与文档差异大）
    assert hyde_retrieve('钱怎么退回来') == ['refund']

    # 3. 多查询：多个改写的融合结果命中退款文档
    assert multi_query_retrieve('怎么退钱') == ['refund']

    # 4. RRF：在两路排名中都靠前的文档，融合后应排在最前
    fused = rrf_fuse([['a', 'b', 'c'], ['b', 'a', 'c']])
    assert fused[0] in ('a', 'b') and set(fused) == {'a', 'b', 'c'}
    assert rrf_fuse([['x', 'y']]) == ['x', 'y']  # 单路排名融合后保持原顺序

    # 5. RRF 的 k 越大，排名差异的影响越小（分数更平滑），但顺序不变
    assert rrf_fuse([['p', 'q']], k=1) == rrf_fuse([['p', 'q']], k=1000)

    # 6. 边界：没有任何文档相关时，仍返回排序结果（不报错）
    assert len(rank_docs('zzzz')) == len(DOCS)
    assert rrf_fuse([]) == []

    print('✅ 查询改写所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 查询改写：HyDE 与多查询 {'*' * 12}", sep='', end='\n\n')
    question = '钱怎么退回来'
    print('原问题直接检索:', retrieve_raw(question))
    print('HyDE 假设答案检索:', hyde_retrieve(question))
    print('多查询（怎么退钱）:', multi_query_retrieve('怎么退钱'))
    run_tests()


if __name__ == '__main__':
    bootstrap()
