"""
[主题]: 向量嵌入与向量索引 (Embedding / 哈希技巧 Hashing Trick / 扁平索引 Flat Index / 元数据过滤)
[来源]: datawhalechina/all-in-rag 第三章「索引构建」(本文件为自行重写的标准库学习版，不依赖 Milvus 与 Embedding 模型)
[难度]: Medium
[前置知识]: 04_all_in_rag/01_retrieval (余弦相似度与 BM25)、字典、zlib 模块

一、主题说明
向量检索的流程分两步：
1. 嵌入 (Embedding): 把文本变成定长的数字向量，语义相近的文本向量也相近；
2. 索引 (Index): 把向量存起来，查询时找出与问题向量最相似的 Top-K。
真实系统用神经网络做 Embedding、用 Milvus / FAISS 做索引。这里用“哈希技巧”代替神经网络：把每个词哈希到固定维度的桶里，计数即为向量。它不懂语义，但足够演示整个索引流程。
注意：必须用 zlib.crc32 而不是内置 hash()，因为内置 hash() 每次运行结果都不同。

二、解法对比（以「找出与问题最相似的 K 个文档」为例）
1. 直观版 brute_force_search: 每次查询都把文档临时向量化再比较。
   - 时间复杂度 O(N × 文档长度)，每次查询都要重算。
2. 进阶版 FlatIndex: 写入时一次性向量化并保存，查询时只做向量比较，并支持元数据过滤。
   - 查询时间复杂度 O(N × D)（D 为向量维度），写入后可重复查询；这就是 Flat 索引，精确但不快。
   - 大规模时才需要 HNSW、IVF 等近似索引（原理请对照原仓库）。

三、真实用途
- 大数据: 亿级文档的向量索引，决定了语义搜索的延迟与成本，选型时要权衡精度与速度。
- 数据分析: 用向量检索做相似工单、相似客户的查找，比关键词匹配更懂语义。
- AI Agent / RAG: 索引是 RAG 的“记忆仓库”，元数据过滤（如只查某部门、某年份）能大幅减少无关结果。
- 全栈开发: 搜索服务上线时，索引的写入、删除、更新接口与一致性是后端设计的核心。
"""

from __future__ import annotations

import math
import re
import zlib
from dataclasses import dataclass, field
from typing import Any

DIM = 64  # 向量维度：维度越高冲突越少，但占用的内存越大


def embed(text: str, dim: int = DIM) -> list[float]:
    """哈希嵌入：每个词用 crc32 映射到一个桶，桶内计数，最后做 L2 归一化。"""
    vector = [0.0] * dim
    for word in re.findall(r'[a-zA-Z0-9]+|[\u4e00-\u9fff]', text.lower()):  # 英文按词、中文按字
        bucket = zlib.crc32(word.encode('utf-8')) % dim  # crc32 结果稳定，每次运行一致
        vector[bucket] += 1.0
    norm = math.sqrt(sum(v * v for v in vector))
    return [v / norm for v in vector] if norm > 0 else vector  # 归一化后点积就是余弦相似度


def dot(a: list[float], b: list[float]) -> float:
    """两个等长向量的点积。"""
    return sum(x * y for x, y in zip(a, b, strict=True))


@dataclass
class Record:
    """索引中的一条记录：文本、向量与元数据（如来源、部门、年份）。"""

    doc_id: str
    text: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


class FlatIndex:
    """扁平索引：保存全部向量，查询时逐条比较，结果精确。"""

    def __init__(self, dim: int = DIM) -> None:
        self.dim = dim
        self.records: dict[str, Record] = {}

    def upsert(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        """写入或更新：同一个 doc_id 再次写入会覆盖旧记录，而不是产生重复数据。"""
        self.records[doc_id] = Record(doc_id, text, embed(text, self.dim), metadata or {})

    def delete(self, doc_id: str) -> bool:
        """删除记录，返回是否真的删除了（不存在时返回 False）。"""
        return self.records.pop(doc_id, None) is not None

    def search(self, query: str, top_k: int = 3, where: dict[str, Any] | None = None) -> list[tuple[str, float]]:
        """检索：先按元数据过滤，再按余弦相似度排序，返回 (doc_id, 分数) 列表。"""
        query_vec = embed(query, self.dim)
        scored: list[tuple[str, float]] = []
        for record in self.records.values():
            if where and any(record.metadata.get(k) != v for k, v in where.items()):
                continue  # 元数据不匹配，直接跳过
            score = dot(query_vec, record.vector)
            if score > 0:  # 完全无关的记录（分数为 0）不返回
                scored.append((record.doc_id, score))
        scored.sort(key=lambda item: (-item[1], item[0]))
        return scored[:top_k]


def brute_force_search(docs: dict[str, str], query: str, top_k: int = 3) -> list[tuple[str, float]]:
    """直观版：每次查询都临时对所有文档做向量化，不保存任何索引。"""
    query_vec = embed(query)
    scored = [(doc_id, dot(query_vec, embed(text))) for doc_id, text in docs.items()]
    scored = [item for item in scored if item[1] > 0]
    scored.sort(key=lambda item: (-item[1], item[0]))
    return scored[:top_k]


DOCS = {
    'd1': '退款政策：签收后七天内可以申请退款',
    'd2': '会员权益：每月两张免运费优惠券',
    'd3': '物流说明：订单发货后三天内送达',
}


def run_tests() -> None:
    """自动化断言测试：覆盖嵌入稳定性、检索排序、增删改、元数据过滤与边界用例。"""
    # 1. 嵌入稳定：同一段文本两次向量化结果完全一致；向量已归一化（长度为 1）
    assert embed('退款政策') == embed('退款政策')
    assert abs(math.sqrt(dot(embed('退款政策'), embed('退款政策'))) - 1.0) < 1e-9

    # 2. 检索排序：查“退款”应该第一个命中 d1
    index = FlatIndex()
    for doc_id, text in DOCS.items():
        index.upsert(doc_id, text, metadata={'dept': 'after_sale' if doc_id == 'd1' else 'ops'})
    assert index.search('怎么退款', top_k=1)[0][0] == 'd1'

    # 3. 与直观版暴力搜索结果一致（同一个嵌入函数，结果必须相同）
    assert index.search('退款', top_k=3) == brute_force_search(DOCS, '退款', top_k=3)

    # 4. 元数据过滤：限定部门后，只能返回该部门的文档
    filtered = index.search('物流 退款 会员', top_k=3, where={'dept': 'ops'})
    assert all(doc_id != 'd1' for doc_id, _ in filtered)

    # 5. 更新：同一 doc_id 再次写入会覆盖旧内容，记录数不增加
    before = len(index.records)
    index.upsert('d1', '全新的内容：优惠券使用规则')
    assert len(index.records) == before
    assert index.search('优惠券', top_k=1)[0][0] == 'd1'

    # 6. 删除：删除后不再被检索到；重复删除返回 False
    assert index.delete('d3') is True
    assert index.delete('d3') is False
    assert all(doc_id != 'd3' for doc_id, _ in index.search('物流', top_k=3))

    # 7. 边界：空查询得到零向量，与任何文档都不相似，结果为空；空索引返回空列表
    #    注意：哈希嵌入存在“桶冲突”，无关查询有时会得到很小的非零分数，这是哈希技巧的已知缺点
    assert index.search('') == []
    assert FlatIndex().search('任何内容') == []

    print('✅ 向量嵌入与索引所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 向量嵌入与索引 {'*' * 12}", sep='', end='\n\n')
    index = FlatIndex()
    for doc_id, text in DOCS.items():
        index.upsert(doc_id, text)
    print(f'已索引 {len(index.records)} 篇文档，向量维度 {index.dim}')
    for query in ['退款', '会员 优惠券', '快递']:
        print(f'查询 {query!r} -> {index.search(query, top_k=2)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
