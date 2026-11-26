"""
[主题]: 检索评估指标：Recall@K、MRR、命中率
[来源]: datawhalechina/all-in-rag 第六章「RAG 系统评估」
[难度]: Easy -> Medium
[前置知识]: list / set、for 循环、dict、函数返回字典

一、主题说明
调 RAG 不能靠感觉「好像准了」，要用同一批带标准答案的问题，对比改动前后的指标：
- Recall@K: 前 K 条结果里，找回了多少比例的相关文档（再对所有问题取平均）；
- MRR (平均倒数排名): 第一个相关文档排第 r 名，得分 1/r，没找到得 0，再取平均；
- 命中率 Hit@K: 前 K 条里至少有一个相关文档的问题占比。

二、解法对比
1. 直观版 recall_at_k_basic: 手写循环，逐个问题累加，便于看懂定义。
2. 进阶版 evaluate: 一次遍历同时算出所有指标并返回 dict，方便做改动前后的对比表。
   - 时间复杂度 O(问题数 * K)，空间复杂度 O(1)

三、真实用途
- RAG / AI Agent: 换分块大小、换 Embedding、加 Rerank 之后，用指标判断是否真的变好。
- 数据分析: 与推荐系统、搜索引擎的离线评估指标完全相同。
"""

from __future__ import annotations


def recall_at_k_basic(rankings: list[list[int]], relevant: list[set[int]], k: int) -> float:
    """直观版：逐个问题计算 Recall@K 再求平均。"""
    if not rankings:
        return 0.0
    total = 0.0
    for ranking, answer_set in zip(rankings, relevant):
        top_k = ranking[:k]
        found = 0
        for doc_id in top_k:
            if doc_id in answer_set:
                found += 1
        total += found / len(answer_set) if answer_set else 0.0
    return total / len(rankings)


def evaluate(rankings: list[list[int]], relevant: list[set[int]], ks: tuple[int, ...] = (1, 3)) -> dict[str, float]:
    """进阶版：一次遍历算出 Recall@K、Hit@K 与 MRR。"""
    if len(rankings) != len(relevant):
        raise ValueError('rankings 与 relevant 的长度必须一致')
    count = len(rankings)
    if count == 0:
        return {}
    metrics: dict[str, float] = {f'recall@{k}': 0.0 for k in ks}
    metrics.update({f'hit@{k}': 0.0 for k in ks})
    reciprocal_total = 0.0

    for ranking, answer_set in zip(rankings, relevant):
        for k in ks:
            hits = len(set(ranking[:k]) & answer_set)
            metrics[f'recall@{k}'] += hits / len(answer_set) if answer_set else 0.0
            metrics[f'hit@{k}'] += 1.0 if hits else 0.0
        for position, doc_id in enumerate(ranking, start=1):
            if doc_id in answer_set:
                reciprocal_total += 1 / position  # 只看第一个相关文档
                break

    result = {name: value / count for name, value in metrics.items()}
    result['mrr'] = reciprocal_total / count
    return result


def run_tests() -> None:
    """自动化断言测试：用手算好的数据校验。"""
    rankings = [[2, 0, 1], [1, 3, 0], [0, 1, 2]]
    relevant = [{2}, {3}, {2}]
    # 三个问题的相关文档分别排第 1、2、3 名

    assert abs(recall_at_k_basic(rankings, relevant, 1) - 1 / 3) < 1e-9
    assert abs(recall_at_k_basic(rankings, relevant, 3) - 1.0) < 1e-9

    result = evaluate(rankings, relevant, ks=(1, 2, 3))
    assert abs(result['recall@1'] - 1 / 3) < 1e-9
    assert abs(result['recall@2'] - 2 / 3) < 1e-9
    assert abs(result['recall@3'] - 1.0) < 1e-9
    assert abs(result['hit@2'] - 2 / 3) < 1e-9
    assert abs(result['mrr'] - (1 + 1 / 2 + 1 / 3) / 3) < 1e-9

    # 多个相关文档：Recall 按比例计算
    multi = evaluate([[5, 6, 7]], [{5, 7, 9}], ks=(3,))
    assert abs(multi['recall@3'] - 2 / 3) < 1e-9

    # 完全没找到：MRR 为 0
    assert evaluate([[1, 2]], [{9}], ks=(2,))['mrr'] == 0.0
    assert evaluate([], []) == {}

    try:
        evaluate([[1]], [])
    except ValueError:
        pass
    else:
        raise AssertionError('长度不一致必须报错')
    print('✅ 检索评估指标所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 检索评估指标 {'*' * 12}", sep='', end='\n\n')
    rankings = [[2, 0, 1], [1, 3, 0], [0, 1, 2]]
    relevant = [{2}, {3}, {2}]
    for name, value in evaluate(rankings, relevant, ks=(1, 2, 3)).items():
        print(f'{name:<10} = {value:.4f}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
