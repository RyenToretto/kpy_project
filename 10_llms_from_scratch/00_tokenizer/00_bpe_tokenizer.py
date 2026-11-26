"""
[主题]: 分词器 (字节级 BPE: Byte-Pair Encoding) 的训练、编码与解码
[来源]: rasbt/LLMs-from-scratch 第 2 章「文本数据处理」(本文件为自行重写的标准库学习版)
[难度]: Medium
[前置知识]: 00_basic 字符串与字典、集合、collections.Counter、bytes 与 UTF-8

一、主题说明
大模型看不懂文字，只认识整数 ID。分词器负责“文本 <-> 整数序列”的互转：
- 按字符切分：词表太大（中文就有上万个字），而且无法处理没见过的字；
- 按字节切分（UTF-8）：词表固定为 256，任何文字都能表示，但序列很长；
- BPE: 从字节开始，反复把最常相邻的一对合并成新 token，在“词表大小”与“序列长度”之间取得平衡。
GPT 系列模型使用的都是字节级 BPE 的变体。

二、解法对比（以「把文本变成 ID 序列」为例）
1. 直观版 char_tokenize: 每个字符一个 ID，建立字典即可。
   - 时间复杂度 O(N)，但遇到词表外的字符就无法编码。
2. 进阶版 train_bpe + encode_bpe: 先按 UTF-8 字节编码，再按合并表依次合并。
   - 训练 O(M * N)（M 为合并次数，N 为长度）；编码 O(M * N)；任何文本都能编码，无未知词。

三、真实用途
- 大数据: 海量语料进入模型前必须统一分词，分词器的版本必须与模型严格一致。
- 数据分析: 文本分析里的词频统计、关键词提取，底层也是分词。
- AI Agent / RAG: Token 数决定了成本与上下文上限，RAG 切块时要按 Token 而不是按字数计算。
- 全栈开发: 前端计算输入长度、后端限流与计费，都需要和模型一致的分词器。
"""

from __future__ import annotations

from collections import Counter

Pair = tuple[int, int]


def get_pair_counts(ids: list[int]) -> Counter[Pair]:
    """统计相邻 token 对的出现次数。"""
    counts: Counter[Pair] = Counter()
    for left, right in zip(ids, ids[1:]):  # 相邻两两配对
        counts[(left, right)] += 1
    return counts


def merge_pair(ids: list[int], pair: Pair, new_id: int) -> list[int]:
    """把序列中所有相邻的 pair 替换为 new_id，从左到右扫描一次。"""
    merged: list[int] = []
    i = 0
    while i < len(ids):
        if i + 1 < len(ids) and (ids[i], ids[i + 1]) == pair:
            merged.append(new_id)  # 命中：两个 token 合成一个
            i += 2
        else:
            merged.append(ids[i])
            i += 1
    return merged


def train_bpe(text: str, num_merges: int) -> tuple[list[Pair], dict[int, bytes]]:
    """训练 BPE：返回合并规则列表（按顺序）与词表（ID -> 字节串）。"""
    ids = list(text.encode('utf-8'))  # 初始 token 就是 0~255 的字节
    vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}
    merges: list[Pair] = []
    for step in range(num_merges):
        counts = get_pair_counts(ids)
        if not counts:  # 没有可合并的相邻对了，提前结束
            break
        # 选出出现次数最多的相邻对；次数相同时取字典序较大的，保证结果可复现
        best = max(counts.items(), key=lambda item: (item[1], item[0]))[0]
        new_id = 256 + step
        ids = merge_pair(ids, best, new_id)
        vocab[new_id] = vocab[best[0]] + vocab[best[1]]  # 新 token 的字节 = 两段拼接
        merges.append(best)
    return merges, vocab


def encode_bpe(text: str, merges: list[Pair]) -> list[int]:
    """编码：先转成字节，再按训练时的顺序依次应用合并规则。"""
    ids = list(text.encode('utf-8'))
    for step, pair in enumerate(merges):
        ids = merge_pair(ids, pair, 256 + step)
    return ids


def decode_bpe(ids: list[int], vocab: dict[int, bytes]) -> str:
    """解码：把每个 ID 还原成字节，拼接后按 UTF-8 解成文字。"""
    raw = b''.join(vocab[i] for i in ids)
    return raw.decode('utf-8')


def char_tokenize(text: str) -> dict[str, int]:
    """直观版：按字符建立词表，遇到新字符就分配一个新编号。"""
    vocab: dict[str, int] = {}
    for ch in text:
        if ch not in vocab:
            vocab[ch] = len(vocab)
    return vocab


def run_tests() -> None:
    """自动化断言测试：覆盖往返一致性、压缩效果、未知文本与边界用例。"""
    corpus = 'low lower lowest 低 低 低 你好你好你好 hello hello'
    merges, vocab = train_bpe(corpus, num_merges=20)

    # 1. 往返一致：编码再解码应得到原文（中英文都要支持）
    for sample in ['lower', '你好世界', 'hello 你好', '']:
        assert decode_bpe(encode_bpe(sample, merges), vocab) == sample

    # 2. 压缩效果：合并后 token 数少于字节数
    sample = 'hello hello'
    assert len(encode_bpe(sample, merges)) < len(sample.encode('utf-8'))

    # 3. 没见过的文字也能编码（字节级兜底，不会出现未知词）
    unseen = '未见过的字 🚀'
    assert decode_bpe(encode_bpe(unseen, merges), vocab) == unseen

    # 4. 合并规则是确定的：同一语料两次训练结果相同
    assert train_bpe(corpus, num_merges=20)[0] == merges

    # 5. 边界：没有可合并的对时提前停止，不会报错
    short_merges, _ = train_bpe('a', num_merges=10)
    assert short_merges == []

    # 6. 直观版字符词表：字符数 = 不同字符的个数
    assert len(char_tokenize('aabbc')) == 3

    print('✅ BPE 分词器所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 字节级 BPE 分词器 {'*' * 12}", sep='', end='\n\n')
    corpus = 'low lower lowest 低 低 低 你好你好你好 hello hello'
    merges, vocab = train_bpe(corpus, num_merges=10)
    print('前 5 条合并规则:', merges[:5])
    sample = 'hello 你好'
    ids = encode_bpe(sample, merges)
    print(f'原文: {sample!r}')
    print(f'字节数: {len(sample.encode("utf-8"))}，BPE token 数: {len(ids)}')
    print('解码还原:', decode_bpe(ids, vocab))
    run_tests()


if __name__ == '__main__':
    bootstrap()
