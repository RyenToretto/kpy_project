"""
[主题]: 大模型 API 基础 (chat 消息结构 / Prompt 模板 / Token 估算 / 密钥从环境变量读取)
[来源]: datawhalechina/llm-universe 第 1~2 章「大模型 API 调用与 Prompt」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 00_basic 语法主线、字典与列表、字符串格式化、os.environ

一、主题说明
绝大多数大模型 API（OpenAI 兼容格式）的输入都是一个 messages 列表：
- system: 给模型的身份与规则，例如“你是一个简洁的客服”；
- user: 用户说的话；
- assistant: 模型之前的回复，用于多轮对话。
Prompt 模板的本质是“把变量填进固定文本”，让同一套指令可以复用。
Token 是模型计费与上下文长度的单位，粗略估算可以帮助控制成本。
API Key 绝不能写进代码，应从环境变量读取。

二、解法对比（以「把用户问题套进客服模板」为例）
1. 直观版 build_prompt_concat: 直接用 + 拼接字符串。
   - 时间复杂度 O(总长度)，但变量多时可读性差，容易漏掉空格或换行。
2. 进阶版 build_prompt_template: str.format_map 填充模板，缺少变量时直接报错，便于发现问题。
   - 时间复杂度 O(总长度)，空间复杂度 O(总长度)
3. 消息版 build_messages: 生成 OpenAI 兼容的 messages 列表，角色清晰，可直接传给 API。

三、真实用途
- 大数据: 批量生成标注任务的 Prompt（如情感分类、实体抽取）时，模板保证每条数据格式一致。
- 数据分析: 用自然语言生成 SQL 或报表解读时，模板把表结构与问题组合在一起。
- AI Agent / RAG: 系统提示词与工具说明本质就是模板，RAG 的上下文拼接也依赖它。
- 全栈开发: 后端调用大模型时，API Key 必须从环境变量或密钥管理服务读取，这是安全底线。
"""

from __future__ import annotations

import os
from typing import Final, TypedDict


class ChatMessage(TypedDict):
    """一条对话消息：role 只能是 system / user / assistant 之一。"""

    role: str
    content: str


SUPPORT_TEMPLATE: Final[str] = (
    '你是一个{tone}的客服助手，回答要控制在{max_words}字以内。\n'
    '用户问题：{question}'
)


def build_prompt_concat(tone: str, max_words: int, question: str) -> str:
    """直观版：用 + 拼接字符串，变量多了容易漏掉或多出空格。"""
    return '你是一个' + tone + '的客服助手，回答要控制在' + str(max_words) + '字以内。\n用户问题：' + question


def build_prompt_template(tone: str, max_words: int, question: str) -> str:
    """进阶版：模板 + format_map，变量缺失时会抛出 KeyError，提前暴露问题。"""
    return SUPPORT_TEMPLATE.format_map({'tone': tone, 'max_words': max_words, 'question': question})


def build_messages(tone: str, max_words: int, question: str) -> list[ChatMessage]:
    """生成 OpenAI 兼容的 messages 列表：system 定规则，user 放问题。"""
    system_text = f'你是一个{tone}的客服助手，回答要控制在{max_words}字以内。'
    return [
        {'role': 'system', 'content': system_text},
        {'role': 'user', 'content': question},
    ]


def estimate_tokens(text: str) -> int:
    """粗略估算 Token 数：中文约 1 字 1 个 Token，英文约 4 个字符 1 个 Token。
    这只是估算，真实计费以模型服务商的 tokenizer 为准。"""
    chinese = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')  # 统计中文字符
    others = len(text) - chinese  # 其余字符（英文、符号、空格）
    return chinese + (others + 3) // 4  # 向上取整，避免低估


def read_api_key(env_name: str = 'DEMO_LLM_API_KEY') -> str | None:
    """从环境变量读取密钥；没有配置时返回 None，由调用方决定如何提示用户。"""
    return os.environ.get(env_name)  # 不写默认值，避免把密钥硬编码进代码


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    # 1. 三种写法的结果完全一致
    args = ('友好', 50, '怎么退款？')
    expected = '你是一个友好的客服助手，回答要控制在50字以内。\n用户问题：怎么退款？'
    assert build_prompt_concat(*args) == expected
    assert build_prompt_template(*args) == expected

    # 2. 消息结构：第一条是 system，第二条是 user
    messages = build_messages(*args)
    assert [m['role'] for m in messages] == ['system', 'user']
    assert messages[1]['content'] == '怎么退款？'

    # 3. 模板缺少变量时必须报错，而不是悄悄输出残缺文本
    try:
        SUPPORT_TEMPLATE.format_map({'tone': '友好'})
    except KeyError:
        pass
    else:
        raise AssertionError('缺少变量时必须抛出 KeyError')

    # 4. Token 估算：纯中文按字数计，英文按每 4 个字符一个 Token 向上取整
    assert estimate_tokens('你好') == 2
    assert estimate_tokens('abcd') == 1
    assert estimate_tokens('abcde') == 2
    assert estimate_tokens('') == 0

    # 5. 密钥从环境变量读取：未设置时返回 None（使用一个不太可能存在的变量名）
    assert read_api_key('KPY_TEST_NOT_EXIST_KEY_123') is None

    print('✅ Prompt 与消息结构所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} Prompt 模板与消息结构 {'*' * 12}", sep='', end='\n\n')
    question = '怎么申请退款？'
    print('拼接版:', build_prompt_concat('友好', 50, question))
    print('模板版:', build_prompt_template('友好', 50, question))
    print('messages:')
    for message in build_messages('友好', 50, question):
        print(f"  [{message['role']}] {message['content']}")
    print(f'估算 Token 数: {estimate_tokens(question)}')
    key = read_api_key()
    print('API Key:', '已配置（已隐藏）' if key else '未配置，请设置环境变量 DEMO_LLM_API_KEY')
    run_tests()


if __name__ == '__main__':
    bootstrap()
