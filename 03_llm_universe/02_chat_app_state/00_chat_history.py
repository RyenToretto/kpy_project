"""
[主题]: 多轮对话的状态管理 (会话历史 / 滑动窗口裁剪 / 清空会话)
[来源]: datawhalechina/llm-universe 第 5 章「搭建 Web 应用」(Streamlit 思路，本文件为自行重写的离线学习版)
[难度]: Easy
[前置知识]: 00_llm_api_basics (messages 结构)、列表切片、字典

一、主题说明
Web 聊天应用的难点不在界面，而在“状态”：
- Streamlit 每次用户操作都会从头重新执行脚本，所以对话历史必须存进 st.session_state 这类会话容器；
- 历史越长，每次发给模型的 Token 越多，成本和延迟都会上升，所以要做窗口裁剪；
- 用户点击“清空会话”时，历史要被完整重置。
本文件用普通字典 session 模拟 session_state，不依赖 Streamlit，离线即可运行。

二、解法对比（以「只保留最近 N 轮对话」为例）
1. 直观版 trim_by_loop: 用 while 循环反复 pop(0) 删除最早的消息。
   - 时间复杂度 O(N^2)（每次 pop(0) 要移动后面所有元素），空间复杂度 O(N)
2. 进阶版 trim_by_slice: 直接切片 messages[-max_messages:]。
   - 时间复杂度 O(N)，空间复杂度 O(max_messages)

三、真实用途
- 大数据: 批量对话日志的截断与分片，同样依赖滑动窗口思想。
- 数据分析: 用户会话行为分析时，按会话 ID 切分事件流，本质是同一套状态管理。
- AI Agent / RAG: Agent 的短期记忆就是有上限的对话窗口，超长时要压缩或丢弃旧内容。
- 全栈开发: 所有带登录状态的 Web 应用都要解决“会话存在哪里、何时过期”的问题。
"""

from __future__ import annotations

from typing import Any

SESSION_KEY = 'chat_messages'  # 会话容器里存放消息列表的键名


def init_session(session: dict[str, Any]) -> None:
    """首次进入页面时初始化会话；已存在则保持不变（对应 Streamlit 的 if key not in session_state）。"""
    if SESSION_KEY not in session:
        session[SESSION_KEY] = []


def add_turn(session: dict[str, Any], user_text: str, reply_text: str) -> None:
    """记录一轮完整对话：先用户、后助手，顺序不能颠倒。"""
    messages: list[dict[str, str]] = session[SESSION_KEY]
    messages.append({'role': 'user', 'content': user_text})
    messages.append({'role': 'assistant', 'content': reply_text})


def trim_by_loop(messages: list[dict[str, str]], max_messages: int) -> list[dict[str, str]]:
    """直观版：不断删除最前面的消息，直到长度不超过上限。"""
    result = list(messages)  # 复制一份，不修改原列表
    while len(result) > max_messages:
        result.pop(0)  # 删除列表头部，后面的元素需要整体前移
    return result


def trim_by_slice(messages: list[dict[str, str]], max_messages: int) -> list[dict[str, str]]:
    """进阶版：切片取最后 max_messages 条，一步完成，并且生成新列表。"""
    if max_messages <= 0:
        return []
    return messages[-max_messages:]


def clear_session(session: dict[str, Any]) -> None:
    """清空会话：整个历史替换为空列表，而不是逐条删除。"""
    session[SESSION_KEY] = []


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例、边界用例与两种裁剪写法的一致性。"""
    session: dict[str, Any] = {}
    init_session(session)
    assert session[SESSION_KEY] == []

    # 1. 多轮对话：每轮追加两条消息，角色顺序正确
    add_turn(session, '你好', '你好，有什么可以帮你？')
    add_turn(session, '怎么退款？', '签收后七天内可以申请。')
    messages = session[SESSION_KEY]
    assert [m['role'] for m in messages] == ['user', 'assistant', 'user', 'assistant']

    # 2. 再次 init 不会清空已有历史
    init_session(session)
    assert len(session[SESSION_KEY]) == 4

    # 3. 两种裁剪写法结果一致：只保留最后 2 条
    assert trim_by_loop(messages, 2) == trim_by_slice(messages, 2)
    assert trim_by_slice(messages, 2)[0]['content'] == '怎么退款？'

    # 4. 边界：上限大于等于长度时原样返回；上限为 0 时为空
    assert trim_by_slice(messages, 10) == messages
    assert trim_by_slice(messages, 0) == []
    assert trim_by_loop(messages, 0) == []

    # 5. 裁剪不修改原历史
    assert len(messages) == 4

    # 6. 清空会话
    clear_session(session)
    assert session[SESSION_KEY] == []

    print('✅ 对话状态管理所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} 多轮对话状态管理 {'*' * 12}", sep='', end='\n\n')
    session: dict[str, Any] = {}
    init_session(session)
    for user_text, reply_text in [
        ('你好', '你好！'),
        ('怎么退款？', '签收后七天内可以申请。'),
        ('会员怎么升级？', '按季度评定等级。'),
    ]:
        add_turn(session, user_text, reply_text)

    print(f"完整历史共 {len(session[SESSION_KEY])} 条")
    recent = trim_by_slice(session[SESSION_KEY], 4)
    print('发送给模型的最近 4 条:')
    for message in recent:
        print(f"  [{message['role']}] {message['content']}")
    clear_session(session)
    print('清空后历史条数:', len(session[SESSION_KEY]))
    run_tests()


if __name__ == '__main__':
    bootstrap()
