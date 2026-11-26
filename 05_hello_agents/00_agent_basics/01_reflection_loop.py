"""
[主题]: Reflection 反思循环 (生成 -> 批评 -> 修订)
[来源]: datawhalechina/hello-agents 第四章「智能体经典范式构建」
[难度]: Medium
[前置知识]: 00_basic/chapter04 (分支)、list、函数作为参数

一、主题说明
Reflection 让 Agent 先写初稿，再由「批评者」按规则挑毛病，最后「修订者」按意见改写，循环直到通过。
这里用规则函数代替大模型：批评者检查「必须包含关键词」和「长度上限」，修订者按意见改写。

二、解法对比
1. 直观版 reflect_basic:
   - 固定循环最多 max_rounds 轮，每轮批评 + 修订，没问题就退出。
   - 时间复杂度 O(轮数 * 文本长度)，空间复杂度 O(1)
2. 进阶版 reflect_traced:
   - 保存每一轮的草稿与意见，方便复盘；
   - 增加「无进展保护」：修订后草稿没变化就停止，避免模型反复输出同一段话空转。
   - 时间复杂度 O(轮数 * 文本长度)，空间复杂度 O(轮数)

三、真实用途
- AI Agent / RAG: 让模型自检答案是否引用了来源、是否超出字数，是提升回答质量的常用手段。
- 全栈开发: 把「规则批评者」换成单元测试或 JSON Schema 校验，就是代码生成 Agent 的自修复循环。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


def critic(draft: str, keywords: tuple[str, ...], max_len: int) -> list[str]:
    """批评者：返回问题列表，空列表表示通过。"""
    issues: list[str] = []
    missing = [word for word in keywords if word not in draft]
    if missing:
        issues.append(f'缺少关键词: {"、".join(missing)}')
    if len(draft) > max_len:
        issues.append(f'超过 {max_len} 字')
    return issues


def reviser(draft: str, issues: list[str], keywords: tuple[str, ...], max_len: int) -> str:
    """修订者：按意见改写。先补关键词，再截断超长部分。"""
    if any(issue.startswith('缺少关键词') for issue in issues):
        draft = '、'.join(keywords) + '入门指南'
    if len(draft) > max_len:
        draft = draft[:max_len]
    return draft


def reflect_basic(draft: str, keywords: tuple[str, ...], max_len: int, max_rounds: int = 3) -> str:
    """直观版：固定轮数的批评 + 修订。"""
    for _ in range(max_rounds):
        issues = critic(draft, keywords, max_len)
        if not issues:
            break
        draft = reviser(draft, issues, keywords, max_len)
    return draft


@dataclass
class Round:
    """一轮反思的记录。"""

    draft: str
    issues: list[str]


@dataclass
class ReflectionResult:
    final_draft: str
    passed: bool
    rounds: list[Round] = field(default_factory=list)


def reflect_traced(
    draft: str,
    keywords: tuple[str, ...],
    max_len: int,
    max_rounds: int = 3,
    revise: Callable[[str, list[str], tuple[str, ...], int], str] = reviser,
) -> ReflectionResult:
    """进阶版：记录轨迹，并在草稿不再变化时提前停止。"""
    result = ReflectionResult(final_draft=draft, passed=False)
    for _ in range(max_rounds):
        issues = critic(draft, keywords, max_len)
        result.rounds.append(Round(draft, issues))
        if not issues:
            result.passed = True
            break
        new_draft = revise(draft, issues, keywords, max_len)
        if new_draft == draft:  # 无进展保护
            break
        draft = new_draft
    result.final_draft = draft
    return result


def run_tests() -> None:
    """自动化断言测试。"""
    keywords = ('RAG', 'Agent')
    bad_draft = '这是一份内容非常非常非常非常非常长的学习资料说明'

    final = reflect_basic(bad_draft, keywords, max_len=20)
    assert critic(final, keywords, 20) == []

    result = reflect_traced(bad_draft, keywords, max_len=20)
    assert result.passed is True
    assert result.final_draft == 'RAG、Agent入门指南'
    assert len(result.rounds) == 2  # 第 1 轮有问题，第 2 轮通过
    assert result.rounds[0].issues and not result.rounds[1].issues

    # 初稿本来就合格：只需要 1 轮
    good = reflect_traced('RAG 与 Agent', keywords, max_len=20)
    assert good.passed and len(good.rounds) == 1

    # 修订者毫无作为时，无进展保护应当停止，而不是空转
    stuck = reflect_traced(bad_draft, keywords, 20, revise=lambda d, i, k, m: d)
    assert stuck.passed is False and len(stuck.rounds) == 1
    print('✅ Reflection 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} Reflection 反思循环 {'*' * 12}", sep='', end='\n\n')
    result = reflect_traced('这是一份内容非常非常非常非常非常长的学习资料说明', ('RAG', 'Agent'), 20)
    for index, item in enumerate(result.rounds, start=1):
        print(f'第 {index} 轮草稿: {item.draft!r}，意见: {item.issues or "通过"}')
    print(f'最终稿: {result.final_draft!r}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
