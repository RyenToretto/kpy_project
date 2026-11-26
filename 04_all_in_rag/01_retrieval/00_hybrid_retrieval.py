"""
[主题]: 混合检索：BM25 + 向量相似度 + RRF 融合
[来源]: datawhalechina/all-in-rag 第四章「检索优化」
[难度]: Medium
[前置知识]: Counter、math.log / math.sqrt、sorted 的 key、正则

一、主题说明
- 稀疏检索 (BM25): 擅长精确关键词命中，如产品型号、专有名词；
- 稠密检索 (向量): 擅长语义相近。这里用「词频向量 + 余弦相似度」代替真实 Embedding，便于离线运行；
- RRF (Reciprocal Rank Fusion): 只看各路排名，score = Σ 1 / (k + rank)，不需要把不同量纲的分数硬凑成一个。

二、解法对比
1. 直观版 rank_by_overlap: 统计查询词与文档词的交集数量，简单但不区分词的稀有度。
2. 进阶版 hybrid_rank: BM25 与向量两路各自排名，再用 RRF 融合。
   - 时间复杂度 O(查询词数 * 文档数)，空间复杂度 O(词表大小)

三、真实用途
- RAG: 混合检索是企业知识库召回的主流方案，比纯向量更稳。
- 大数据 / 搜索: Elasticsearch 的 BM25 加向量字段，本质是同一思路。
"""

from __future__ import annotations

import math
import re
from collections import Counter

CORPUS = [
    'Python 的 list 是可变序列，可以 append 元素',
    'FastAPI 是高性能的 Python Web 框架',
    'RAG 通过检索外部知识来减少大模型幻觉',
    'Milvus 是一个向量数据库，用于存储 embedding',
    '今天长沙天气晴朗，适合出门散步',
]


def tokenize(text: str) -> list[str]:
    """英文按单词；中文按单字 + 相邻双字，兼顾召回与精度。"""
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    for run in re.findall(r'[\u4e00-\u9fff]+', text):
        tokens.extend(run)  # 单字
        tokens.extend(run[i : i + 2] for i in range(len(run) - 1))  # 双字
    return tokens


def rank_by_overlap(query: str, docs: list[str]) -> list[int]:
    """直观版：按词交集数量排序，数量相同按原顺序。"""
    query_set = set(tokenize(query))
    scores = [len(query_set & set(tokenize(doc))) for doc in docs]
    return sorted(range(len(docs)), key=lambda idx: (-scores[idx], idx))


class BM25:
    """BM25 打分：词越稀有权重越高，文档越长越要打折。"""

    def __init__(self, docs: list[str], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.doc_tokens = [tokenize(doc) for doc in docs]
        self.doc_counts = [Counter(tokens) for tokens in self.doc_tokens]
        self.avg_len = sum(len(tokens) for tokens in self.doc_tokens) / len(docs)
        doc_freq: Counter[str] = Counter()
        for counts in self.doc_counts:
            doc_freq.update(counts.keys())
        total_docs = len(docs)
        self.idf = {
            term: math.log((total_docs - freq + 0.5) / (freq + 0.5) + 1) for term, freq in doc_freq.items()
        }

    def score(self, query_tokens: list[str], idx: int) -> float:
        counts, doc_len = self.doc_counts[idx], len(self.doc_tokens[idx])
        total = 0.0
        for term in set(query_tokens):
            freq = counts.get(term, 0)
            if freq == 0:
                continue
            norm = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avg_len)
            total += self.idf[term] * freq * (self.k1 + 1) / norm
        return total

    def rank(self, query: str) -> list[int]:
        query_tokens = tokenize(query)
        scores = [self.score(query_tokens, idx) for idx in range(len(self.doc_tokens))]
        return sorted(range(len(scores)), key=lambda idx: (-scores[idx], idx))


def cosine_rank(query: str, docs: list[str]) -> list[int]:
    """向量排名：词频向量的余弦相似度。"""

    def cosine(a: Counter[str], b: Counter[str]) -> float:
        dot = sum(a[term] * b.get(term, 0) for term in a)
        norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
        return dot / norm if norm else 0.0

    query_vec = Counter(tokenize(query))
    scores = [cosine(query_vec, Counter(tokenize(doc))) for doc in docs]
    return sorted(range(len(docs)), key=lambda idx: (-scores[idx], idx))


def rrf_fuse(rankings: list[list[int]], k: int = 60) -> list[int]:
    """RRF 融合多路排名：名次越靠前贡献越大。"""
    fused: Counter[int] = Counter()
    for ranking in rankings:
        for position, doc_id in enumerate(ranking, start=1):
            fused[doc_id] += 1 / (k + position)
    return sorted(fused, key=lambda doc_id: (-fused[doc_id], doc_id))


def hybrid_rank(query: str, docs: list[str]) -> list[int]:
    """进阶版：BM25 + 向量两路排名，再 RRF 融合。"""
    return rrf_fuse([BM25(docs).rank(query), cosine_rank(query, docs)])


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [('向量数据库', 3), ('RAG 如何减少幻觉', 2), ('Python web 框架', 1), ('list append', 0)]
    for query, expected in cases:
        assert hybrid_rank(query, CORPUS)[0] == expected, f'混合检索失败: {query}'
        assert BM25(CORPUS).rank(query)[0] == expected, f'BM25 失败: {query}'
    assert rank_by_overlap('向量数据库', CORPUS)[0] == 3

    # RRF: 两路都认为 7 号靠前时，它应该胜出
    assert rrf_fuse([[7, 1, 2], [7, 2, 1]])[0] == 7
    assert rrf_fuse([[1, 2], [2, 1]]) == [1, 2]  # 完全对称时按 id 稳定排序
    print('✅ 混合检索所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 混合检索 BM25 + 向量 + RRF {'*' * 12}", sep='', end='\n\n')
    for query in ('向量数据库', 'RAG 如何减少幻觉'):
        ranking = hybrid_rank(query, CORPUS)
        print(f'查询 {query!r} -> 最相关文档: {CORPUS[ranking[0]]}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
