"""
[主题]: 个人知识库问答 (文档切块 / 关键词检索 / 上下文拼接 / 带引用的回答)
[来源]: datawhalechina/llm-universe 第 3~4 章「构建知识库助手」(本文件为自行重写的学习版)
[难度]: Medium
[前置知识]: 00_llm_api_basics (Prompt 模板)、列表推导式、集合运算、dataclass

一、主题说明
RAG（检索增强生成）的最小闭环只有四步：
1. 切块: 把长文档切成小段，便于检索并控制上下文长度；
2. 检索: 根据用户问题找出最相关的若干段；
3. 拼接: 把检索结果放进 Prompt，要求模型“只根据资料回答”；
4. 生成: 调用大模型，并附上引用的来源，方便人工核对。
本文件用关键词重叠度代替向量检索，完全离线可运行；“大模型”用规则版假模型代替，接口形态与真实 API 一致。

二、解法对比（以「在文档里找答案」为例）
1. 直观版 search_naive: 对每个文档做 `in` 子串查找，只要包含问题就返回。
   - 时间复杂度 O(文档数 * 文档长度)，问题一长就几乎搜不到。
2. 进阶版 search_by_keywords: 切块后统计关键词重叠数，按得分排序取 Top-K。
   - 时间复杂度 O(块数 * 关键词数)，空间复杂度 O(块数)；能容忍措辞变化。

三、真实用途
- 大数据: 企业文档、工单、日志的检索入口，先用关键词召回再做精排，成本最低。
- 数据分析: 把报表说明文档做成知识库，业务人员可以直接问“这个指标怎么算”。
- AI Agent / RAG: 这就是 RAG 的骨架，后续只需把关键词检索换成向量检索即可升级。
- 全栈开发: 产品文档问答机器人、客服知识库，都是这套结构加上 Web 界面。
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """一段文本块：记录来源文档名与块序号，回答时用来做引用。"""

    source: str
    index: int
    text: str


def split_into_chunks(source: str, text: str, chunk_size: int = 40) -> list[Chunk]:
    """按固定字数切块；相邻块之间没有重叠，演示最简单的切块方式。"""
    chunks: list[Chunk] = []
    for start in range(0, len(text), chunk_size):  # 步长为 chunk_size，依次取出每一段
        piece = text[start:start + chunk_size].strip()
        if piece:  # 跳过全是空白的块
            chunks.append(Chunk(source=source, index=len(chunks), text=piece))
    return chunks


def tokenize(text: str) -> set[str]:
    """极简分词：英文按单词、中文按单字，全部转小写后放进集合。"""
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())  # 英文和数字
    hanzi = re.findall(r'[\u4e00-\u9fff]', text)  # 每个汉字单独成词
    return set(words) | set(hanzi)


def search_naive(documents: dict[str, str], question: str) -> list[str]:
    """直观版：只要问题整句出现在文档里才算命中，措辞稍有变化就找不到。"""
    return [name for name, text in documents.items() if question in text]


def search_by_keywords(chunks: list[Chunk], question: str, top_k: int = 2) -> list[Chunk]:
    """进阶版：统计每个块与问题共有的关键词数，按得分从高到低取前 top_k 个。"""
    query_terms = tokenize(question)
    scored: list[tuple[int, Chunk]] = []
    for chunk in chunks:
        overlap = len(query_terms & tokenize(chunk.text))  # 集合交集 = 共有关键词
        if overlap > 0:  # 完全无关的块不参与排序
            scored.append((overlap, chunk))
    scored.sort(key=lambda pair: (-pair[0], pair[1].source, pair[1].index))  # 得分降序，同分按来源稳定排序
    return [chunk for _, chunk in scored[:top_k]]


def build_context_prompt(question: str, hits: list[Chunk]) -> str:
    """把检索到的块拼成资料区，并要求模型只依据资料回答。"""
    if not hits:
        return f'资料中没有相关内容。\n问题：{question}'
    materials = '\n'.join(f'[{h.source}#{h.index}] {h.text}' for h in hits)
    return f'请只根据下面的资料回答问题，资料不足时请说“不知道”。\n资料：\n{materials}\n问题：{question}'


def fake_llm(prompt: str) -> str:
    """规则版假模型：资料中有内容就复述第一条，否则回答“不知道”。真实场景这里换成 API 调用。"""
    if '没有相关内容' in prompt:
        return '不知道'
    first_line = prompt.split('\n')[2]  # 第一条资料所在行
    return f'根据资料：{first_line.split("] ", 1)[1]}'


def answer_question(chunks: list[Chunk], question: str) -> tuple[str, list[str]]:
    """完整流程：检索 -> 拼接 -> 生成，返回回答与引用列表。"""
    hits = search_by_keywords(chunks, question)
    answer = fake_llm(build_context_prompt(question, hits))
    citations = [f'{h.source}#{h.index}' for h in hits]
    return answer, citations


DOCS = {
    '退款说明.md': '商品签收后七天内可以申请无理由退款，退款会在三个工作日内原路返回。',
    '会员规则.md': '会员每月可以免费使用两次优惠券，会员等级每季度重新评定一次。',
}


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例、无关问题与边界用例。"""
    chunks = [c for name, text in DOCS.items() for c in split_into_chunks(name, text)]
    assert all(len(c.text) <= 40 for c in chunks)  # 每块不超过 40 字

    # 1. 关键词检索能命中正确的文档
    hits = search_by_keywords(chunks, '如何申请退款')
    assert hits and hits[0].source == '退款说明.md'

    # 2. 直观版子串查找：措辞一变就找不到，关键词版仍能找到
    assert search_naive(DOCS, '如何申请退款') == []
    assert search_naive(DOCS, '退款') == ['退款说明.md']

    # 3. 完整问答：回答带引用，且引用来源正确
    answer, citations = answer_question(chunks, '会员每月能用几次优惠券')
    assert citations and citations[0].startswith('会员规则.md')
    assert '优惠券' in answer

    # 4. 无关问题：没有命中，回答“不知道”（注意：不能含“天”，否则会命中“七天内”）
    answer, citations = answer_question(chunks, '火星探测器')
    assert answer == '不知道' and citations == []

    # 5. 边界：空文本不产生任何块；空问题不会命中
    assert split_into_chunks('空.md', '   ') == []
    assert search_by_keywords(chunks, '') == []

    print('✅ 知识库问答所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 个人知识库问答 {'*' * 12}", sep='', end='\n\n')
    chunks = [c for name, text in DOCS.items() for c in split_into_chunks(name, text)]
    print(f'共切出 {len(chunks)} 个块')
    for question in ['如何申请退款', '会员等级多久评定一次', '火星探测器']:
        answer, citations = answer_question(chunks, question)
        print(f'\n问：{question}\n答：{answer}\n引用：{citations or "无"}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
