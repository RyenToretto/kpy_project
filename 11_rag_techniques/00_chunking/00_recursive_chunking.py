"""
[主题]: RAG 切块策略 (递归分隔符切块 / 固定重叠 / 基于相似度断点的语义切块)
[来源]: NirDiamant/RAG_Techniques 「Chunking」章节思路 (本文件为自行重写的标准库学习版)
[难度]: Medium
[前置知识]: 04_all_in_rag/00_data_prep (固定切块与句子切块)、递归函数、集合与字典

一、主题说明
切块质量决定了 RAG 能不能找到答案：
- 块太大: 一个块里混入多个主题，检索时相似度被“稀释”；
- 块太小: 上下文断裂，答案被拆散在多个块里；
- 硬切（每 N 个字符）会把句子从中间切断，语义被破坏。
更好的做法是“按自然边界切”：先按段落，再按句子，最后才按字符，并在相邻块之间保留少量重叠。

二、解法对比（以「把长文切成不超过 N 字的块」为例）
1. 直观版 hard_split: 每 N 个字符切一刀。
   - 时间复杂度 O(L)，但经常切断句子与词语。
2. 进阶版 recursive_split: 依次尝试 段落 -> 换行 -> 句号 -> 空格 -> 硬切，能按边界切就不硬切。
   - 时间复杂度 O(L * 分隔符层数)，空间复杂度 O(L)；块边界尽量落在自然停顿处。
3. 语义版 semantic_split: 相邻句子的相似度骤降时才断开，同一主题的句子保持在一起。
   - 时间复杂度 O(句子数 * 词表)，需要为每句计算向量。

三、真实用途
- 大数据: 海量文档入库前的预处理，切块策略直接影响向量索引的规模与召回质量。
- 数据分析: 长报告、财报、会议纪要的分段，决定了问答的粒度。
- AI Agent / RAG: 切块是 RAG 效果的第一杠杆，比换模型往往更有效。
- 全栈开发: 文档上传功能里的“解析 -> 切块 -> 入库”流水线，就是这套逻辑。
"""

from __future__ import annotations

import math
from collections import Counter

DEFAULT_SEPARATORS = ['\n\n', '\n', '。', ' ']  # 从大到小尝试的自然边界


def hard_split(text: str, max_chars: int) -> list[str]:
    """直观版：每 max_chars 个字符硬切一刀，不考虑句子边界。"""
    return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]


def recursive_split(text: str, max_chars: int, separators: list[str] | None = None) -> list[str]:
    """递归切块：优先用大边界（段落）切，超长的段再用小边界（句子）切，最后才硬切。"""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]
    seps = DEFAULT_SEPARATORS if separators is None else separators
    if not seps:  # 没有可用分隔符了，只能硬切
        return hard_split(text, max_chars)
    sep, rest = seps[0], seps[1:]
    if sep not in text:  # 当前分隔符不存在，直接试下一级
        return recursive_split(text, max_chars, rest)

    chunks: list[str] = []
    current = ''
    for piece in text.split(sep):
        candidate = piece if not current else current + sep + piece  # 尽量把多段合并到一个块里
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)  # 装不下了，先把已有内容输出
        if len(piece) > max_chars:  # 单段本身就超长，递归到更小的分隔符
            chunks.extend(recursive_split(piece, max_chars, rest))
            current = ''
        else:
            current = piece
    if current:
        chunks.append(current)
    return chunks


def add_overlap(chunks: list[str], overlap: int) -> list[str]:
    """给每个块（除第一个）前面拼上上一个块的末尾 overlap 个字符，减少边界处的信息丢失。"""
    if overlap <= 0 or len(chunks) <= 1:
        return list(chunks)
    result = [chunks[0]]
    for previous, current in zip(chunks, chunks[1:]):
        result.append(previous[-overlap:] + current)
    return result


def bag_of_chars(text: str) -> Counter[str]:
    """字符袋：用字符频次近似一个句子的向量（中文场景下足够直观）。"""
    return Counter(ch for ch in text if not ch.isspace() and ch not in '，。！？；：')


def cosine(a: Counter[str], b: Counter[str]) -> float:
    """余弦相似度：两个向量夹角的余弦，越接近 1 越相似。"""
    dot = sum(a[key] * b[key] for key in a.keys() & b.keys())
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def semantic_split(text: str, threshold: float = 0.2, max_chars: int = 80) -> list[str]:
    """语义切块：相邻句子相似度低于阈值（主题变化）或超过长度上限时才断开。"""
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    if not sentences:
        return []
    chunks: list[str] = []
    current = sentences[0]
    for previous, sentence in zip(sentences, sentences[1:]):
        similarity = cosine(bag_of_chars(previous), bag_of_chars(sentence))
        if similarity < threshold or len(current) + len(sentence) > max_chars:
            chunks.append(current + '。')
            current = sentence
        else:
            current = current + '。' + sentence
    chunks.append(current + '。')
    return chunks


DOC = (
    '退款政策说明\n\n'
    '商品签收后七天内可以申请无理由退款。退款申请提交后三个工作日内处理完成。\n'
    '会员权益介绍\n\n'
    '会员每月可以享受两次免运费服务。会员等级每季度重新评定一次。'
)


def run_tests() -> None:
    """自动化断言测试：覆盖块大小上限、内容完整、重叠与语义断点。"""
    # 1. 递归切块：每块都不超过上限
    chunks = recursive_split(DOC, max_chars=30)
    assert chunks and all(len(c) <= 30 for c in chunks)

    # 2. 边界优先：递归切块不会把“退款政策说明”这种标题从中间切断
    assert any(c.startswith('退款政策说明') for c in chunks)

    # 3. 内容完整：去掉分隔符后，所有字符都保留下来（没有丢字）
    original = DOC.replace('\n', '').replace('。', '')
    rebuilt = ''.join(chunks).replace('\n', '').replace('。', '')
    assert sorted(rebuilt) == sorted(original)

    # 4. 对比：硬切会在句子中间断开（第一块不以句号结尾），递归切块则不会
    hard = hard_split(DOC, max_chars=30)
    assert all(len(c) <= 30 for c in hard)
    assert not hard[0].endswith('。')  # 第一块停在了“申请”中间，句子被拦腰截断

    # 5. 重叠：每个块（除第一块）前面都带上了前一块的末尾字符
    overlapped = add_overlap(['abcdef', 'ghijkl'], overlap=2)
    assert overlapped == ['abcdef', 'efghijkl']

    # 6. 语义切块：主题明显不同的两句会被断开
    semantic = semantic_split('苹果很好吃。苹果很甜。火箭发射成功。卫星进入轨道。', threshold=0.3, max_chars=200)
    assert len(semantic) >= 2

    # 7. 边界：空文本返回空列表
    assert recursive_split('   ', 10) == [] and semantic_split('', 0.2) == []

    print('✅ RAG 切块策略所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} RAG 切块策略 {'*' * 12}", sep='', end='\n\n')
    print('硬切（每 30 字）:')
    for item in hard_split(DOC, 30)[:3]:
        print(f'  | {item!r}')
    print('\n递归切块（按段落 -> 句子 -> 字符）:')
    for item in recursive_split(DOC, 30):
        print(f'  | {item}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
