"""
[主题]: 项目实战：把切块、索引、混合检索、带引用的回答与评估串成一条可测试的 RAG 流水线
[来源]: datawhalechina/all-in-rag 第八章「项目实战」(本文件为自行重写的标准库学习版，所有组件均离线可运行)
[难度]: Hard
[前置知识]: 04_all_in_rag/00~03 全部内容（切块、混合检索、评估、向量索引）、dataclass、字典与集合

一、主题说明
前面几章学的是零件，这一章把零件装成一台机器。一条完整的 RAG 流水线包括：
1. 入库 ingest: 文档 -> 切块 -> 向量化 -> 写入索引（同一文档重复入库时要覆盖，不能重复）；
2. 检索 retrieve: 向量相似度 + 关键词重叠，用 RRF 融合两路排名，并支持元数据过滤；
3. 生成 answer: 抽取最相关的句子作为回答（真实系统中这里交给大模型），并附上引用来源；
4. 评估 evaluate: 用带标注的问题集计算 Recall@K，量化检索效果。
每个环节都可以单独替换，这正是工程化 RAG 的核心思想。

二、解法对比（以「回答一个问题」为例）
1. 直观版 answer_naive: 把整库文本全部拼进 Prompt，再让模型回答。
   - 上下文随文档增长线性膨胀，超出模型长度上限就会失败，成本也高。
2. 进阶版 RagPipeline.query: 先检索出 Top-K 个相关块，只把它们交给生成环节，并保留引用。
   - 时间复杂度 O(块数 × 词表)（检索），生成的上下文长度恒定，可控、可追溯。

三、真实用途
- 大数据: 企业文档库的问答服务，入库要幂等（重复导入不产生脏数据），检索要可评估。
- 数据分析: 报表说明、指标口径文档的问答，回答必须带引用，方便业务人员核对。
- AI Agent / RAG: 这就是 Agent 的“知识工具”，上线前必须有评估集来证明它真的变好了。
- 全栈开发: 搭建知识库产品时，入库、检索、回答、评估四个接口正好对应后端的四个模块。
"""

from __future__ import annotations

import math
import re
import zlib
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

DIM = 128
RRF_K = 60


@dataclass(frozen=True)
class Chunk:
    """一个文本块：归属的文档 ID、序号、正文与元数据。"""

    doc_id: str
    index: int
    text: str
    metadata: tuple[tuple[str, Any], ...] = field(default_factory=tuple)

    def meta(self, key: str) -> Any:
        """读取元数据中的某个字段。"""
        return dict(self.metadata).get(key)


@dataclass(frozen=True)
class Answer:
    """回答结果：正文与引用的 (doc_id, 块序号) 列表。没有依据时引用为空。"""

    text: str
    citations: tuple[tuple[str, int], ...]


def tokenize(text: str) -> list[str]:
    """分词：英文与数字按词，中文按字，统一转小写。"""
    return re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]', text.lower())


def embed(text: str, dim: int = DIM) -> list[float]:
    """哈希向量：crc32 稳定映射到桶，计数后 L2 归一化。"""
    vector = [0.0] * dim
    for token in tokenize(text):
        vector[zlib.crc32(token.encode('utf-8')) % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vector))
    return [v / norm for v in vector] if norm > 0 else vector


def split_sentences(text: str, max_chars: int = 60) -> list[str]:
    """切块：按句号切成句子，再把相邻句子打包到不超过 max_chars 的块里。"""
    sentences = [s.strip() + '。' for s in text.split('。') if s.strip()]
    chunks: list[str] = []
    current = ''
    for sentence in sentences:
        if current and len(current) + len(sentence) > max_chars:
            chunks.append(current)
            current = sentence
        else:
            current += sentence
    if current:
        chunks.append(current)
    return chunks


def rrf_fuse(rankings: list[list[tuple[str, int]]], k: int = RRF_K) -> list[tuple[str, int]]:
    """RRF 融合：每个块在各路排名中得到 1/(k+rank) 分，累加后降序。"""
    scores: Counter[tuple[str, int]] = Counter()
    for ranking in rankings:
        for rank, key in enumerate(ranking, start=1):
            scores[key] += 1.0 / (k + rank)
    return [key for key, _ in sorted(scores.items(), key=lambda item: (-item[1], item[0]))]


class RagPipeline:
    """RAG 流水线：内部用字典保存块，key 为 (doc_id, 序号)，便于按文档覆盖更新。"""

    def __init__(self) -> None:
        self.chunks: dict[tuple[str, int], Chunk] = {}
        self.vectors: dict[tuple[str, int], list[float]] = {}

    def ingest(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> int:
        """入库（幂等）：先删除该文档的旧块，再写入新块，返回写入的块数。"""
        self.delete(doc_id)
        meta_items = tuple(sorted((metadata or {}).items()))
        for index, piece in enumerate(split_sentences(text)):
            key = (doc_id, index)
            self.chunks[key] = Chunk(doc_id, index, piece, meta_items)
            self.vectors[key] = embed(piece)
        return sum(1 for key in self.chunks if key[0] == doc_id)

    def delete(self, doc_id: str) -> None:
        """删除某个文档的全部块。"""
        for key in [k for k in self.chunks if k[0] == doc_id]:
            del self.chunks[key]
            del self.vectors[key]

    def retrieve(self, question: str, top_k: int = 2, where: dict[str, Any] | None = None) -> list[Chunk]:
        """混合检索：向量排名 + 关键词排名，用 RRF 融合。元数据过滤在排名前完成。"""
        candidates = [
            key for key, chunk in self.chunks.items()
            if not where or all(chunk.meta(k) == v for k, v in where.items())
        ]
        query_vec = embed(question)
        query_terms = set(tokenize(question))

        vector_rank = sorted(
            (key for key in candidates if sum(a * b for a, b in zip(query_vec, self.vectors[key])) > 0),
            key=lambda key: (-sum(a * b for a, b in zip(query_vec, self.vectors[key])), key),
        )
        keyword_rank = sorted(
            (key for key in candidates if query_terms & set(tokenize(self.chunks[key].text))),
            key=lambda key: (-len(query_terms & set(tokenize(self.chunks[key].text))), key),
        )
        fused = rrf_fuse([vector_rank, keyword_rank])
        return [self.chunks[key] for key in fused[:top_k]]

    def answer(self, question: str, top_k: int = 2, where: dict[str, Any] | None = None) -> Answer:
        """生成回答（抽取式）：取检索结果中与问题重叠最多的一句，并附上引用。"""
        hits = self.retrieve(question, top_k=top_k, where=where)
        terms = set(tokenize(question))
        hits = [h for h in hits if terms & set(tokenize(h.text))]  # 没有任何关键词命中的块不作为依据
        if not hits:
            return Answer('资料中没有相关信息。', ())
        best = max(hits, key=lambda h: len(terms & set(tokenize(h.text))))
        citations = tuple((h.doc_id, h.index) for h in hits)
        return Answer(best.text, citations)


def recall_at_k(pipeline: RagPipeline, eval_set: list[tuple[str, str]], k: int = 2) -> float:
    """评估：每个问题的标准来源文档是否出现在 Top-K 结果中，返回命中比例。"""
    if not eval_set:
        return 0.0
    hit = 0
    for question, expected_doc in eval_set:
        sources = {chunk.doc_id for chunk in pipeline.retrieve(question, top_k=k)}
        hit += expected_doc in sources
    return hit / len(eval_set)


DOCS = {
    'refund': '商品签收后七天内可以申请退款。退款原路返回，三个工作日内到账。',
    'member': '会员每月可以享受两次免运费服务。会员等级每季度重新评定一次。',
    'logistics': '订单发货后可以在物流页面查看快递轨迹。一般三天内送达。',
}
EVAL_SET = [
    ('怎么申请退款', 'refund'),
    ('会员有什么权益', 'member'),
    ('快递多久能送到', 'logistics'),
]


def build_pipeline() -> RagPipeline:
    """构造一个已入库示例文档的流水线。"""
    pipeline = RagPipeline()
    for doc_id, text in DOCS.items():
        pipeline.ingest(doc_id, text, metadata={'team': 'support' if doc_id != 'logistics' else 'ops'})
    return pipeline


def run_tests() -> None:
    """自动化断言测试：覆盖入库幂等、检索、带引用回答、元数据过滤、评估与无依据兜底。"""
    pipeline = build_pipeline()

    # 1. 切块：长文被切成若干块，每块不超过上限（句子不会被拦腰截断）
    pieces = split_sentences(DOCS['refund'])
    assert all(p.endswith('。') for p in pieces) and len(pieces) >= 1

    # 2. 检索与回答：问退款应引用 refund 文档，并给出包含“退款”的句子
    answer = pipeline.answer('怎么申请退款')
    assert '退款' in answer.text
    assert answer.citations and answer.citations[0][0] == 'refund'

    # 3. 评估：样例集的 Recall@2 应为 1.0
    assert recall_at_k(pipeline, EVAL_SET, k=2) == 1.0

    # 4. 元数据过滤：只在 ops 团队里检索时，退款文档不应出现
    filtered = pipeline.retrieve('怎么申请退款', top_k=3, where={'team': 'ops'})
    assert all(chunk.doc_id != 'refund' for chunk in filtered)

    # 5. 入库幂等：重复入库同一文档，旧块被整体替换，总块数只按差值变化
    new_text = '全新规则：优惠券可叠加使用。'
    total_before = len(pipeline.chunks)
    refund_before = sum(1 for c in pipeline.chunks.values() if c.doc_id == 'refund')
    pipeline.ingest('refund', new_text)
    refund_after = sum(1 for c in pipeline.chunks.values() if c.doc_id == 'refund')
    assert refund_after == len(split_sentences(new_text))  # 只剩新文本产生的块
    assert len(pipeline.chunks) == total_before - refund_before + refund_after
    assert all('退款' not in c.text for c in pipeline.chunks.values() if c.doc_id == 'refund')

    # 6. 删除文档后，它的块全部消失
    pipeline.delete('member')
    assert all(chunk.doc_id != 'member' for chunk in pipeline.chunks.values())

    # 7. 无依据兜底：与资料完全无关的问题，回答“没有相关信息”，且没有引用
    no_info = pipeline.answer('火星探测器')
    assert no_info.text == '资料中没有相关信息。' and no_info.citations == ()

    print('✅ RAG 项目流水线所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} RAG 项目实战流水线 {'*' * 12}", sep='', end='\n\n')
    pipeline = build_pipeline()
    print(f'已入库文档 {len(DOCS)} 篇，共 {len(pipeline.chunks)} 个块')
    for question in ['怎么申请退款', '会员有什么权益', '火星探测器']:
        result = pipeline.answer(question)
        print(f'问：{question}\n答：{result.text}\n引用：{list(result.citations) or "无"}\n')
    print(f'EVAL Recall@2 = {recall_at_k(pipeline, EVAL_SET, k=2):.2f}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
