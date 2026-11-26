"""
[主题]: RAG 文本分块 (Chunking)：定长重叠 vs 按句子打包
[来源]: datawhalechina/all-in-rag 第二章「数据准备」
[难度]: Easy -> Medium
[前置知识]: 字符串切片、range 步长、re 正则、list

一、主题说明
大模型上下文有限，长文档必须先切成小块再建索引。切得不好，检索就会丢信息或带进噪声。

二、解法对比
1. 直观版 chunk_fixed（定长 + 重叠）:
   - 每 size 个字符切一块，相邻块重叠 overlap 个字符，避免句子恰好在边界被截断而丢上下文。
   - 缺点: 可能把一句话从中间切开。
   - 时间复杂度 O(n)，空间复杂度 O(n)
2. 进阶版 chunk_by_sentence（按句子打包）:
   - 先按句号等标点拆句，再把相邻句子贪心装进不超过 max_chars 的块里；
   - 超长单句才强制硬切。语义更完整，更适合问答检索。
   - 时间复杂度 O(n)，空间复杂度 O(n)

三、真实用途
- RAG: 块大小与重叠是召回率最常调的两个参数。
- 大数据 / 数据分析: 日志、合同、客服记录入库前都要先分块。
- AI Agent: 长对话历史压缩为摘要前，同样需要按语义边界切分。
"""

from __future__ import annotations

import re


def chunk_fixed(text: str, size: int, overlap: int) -> list[str]:
    """定长分块：每块 size 个字符，相邻块重叠 overlap 个字符。"""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError('size 必须为正数，且 0 <= overlap < size')
    chunks: list[str] = []
    step = size - overlap  # 每次向前滑动的距离
    for start in range(0, len(text), step):
        chunks.append(text[start : start + size])
        if start + size >= len(text):  # 已经覆盖到末尾，避免产生被上一块完全包含的尾巴
            break
    return chunks


def chunk_by_sentence(text: str, max_chars: int) -> list[str]:
    """按句子打包：尽量不拆句，装不下再另起一块；单句超长才硬切。"""
    if max_chars <= 0:
        raise ValueError('max_chars 必须为正数')
    sentences = re.findall(r'[^。！？!?.\n]+[。！？!?.]?', text)
    chunks: list[str] = []
    current = ''
    for sentence in sentences:
        if len(sentence) > max_chars:  # 单句过长：先收尾当前块，再硬切这句
            if current:
                chunks.append(current)
                current = ''
            for start in range(0, len(sentence), max_chars):
                chunks.append(sentence[start : start + max_chars])
            continue
        if len(current) + len(sentence) <= max_chars:
            current += sentence
        else:
            chunks.append(current)
            current = sentence
    if current:
        chunks.append(current)
    return chunks


def run_tests() -> None:
    """自动化断言测试。"""
    assert chunk_fixed('abcdefghij', size=4, overlap=1) == ['abcd', 'defg', 'ghij']
    assert chunk_fixed('abc', size=10, overlap=2) == ['abc']
    assert chunk_fixed('', size=4, overlap=1) == []
    try:
        chunk_fixed('abc', size=3, overlap=3)
    except ValueError:
        pass
    else:
        raise AssertionError('overlap >= size 必须报错')

    text = '第一句。第二句。第三句。'
    assert chunk_by_sentence(text, 6) == ['第一句。', '第二句。', '第三句。']
    assert chunk_by_sentence(text, 8) == ['第一句。第二句。', '第三句。']
    assert chunk_by_sentence('', 8) == []

    long_text = '这是一个没有任何标点而且特别特别长的句子' + '。短句。'
    pieces = chunk_by_sentence(long_text, 8)
    assert all(len(piece) <= 8 for piece in pieces)
    assert ''.join(pieces) == long_text  # 切完再拼回去，内容一个字都不能丢
    print('✅ 文本分块所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} RAG 文本分块 {'*' * 12}", sep='', end='\n\n')
    sample = 'RAG 先检索资料。再让大模型回答。这样可以减少幻觉。'
    print(f'定长重叠: {chunk_fixed(sample, size=12, overlap=4)}')
    print(f'按句子:   {chunk_by_sentence(sample, max_chars=18)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
