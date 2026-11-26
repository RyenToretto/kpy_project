"""
[题目编号]: LeetCode 146. LRU 缓存 (LRU Cache)
[难度]: Medium (大厂后端/AI 基础设施面试 TOP 3 高频题)
[所属专题]: 06_linked_list
[前置知识]: class、dict、双向链表节点插入与删除 / collections.OrderedDict

一、题目描述
请你设计并实现一个满足「最近最少使用 (Least Recently Used, LRU)」缓存约束的数据结构：
- `LRUCache(capacity)`: 以正整数作为容量初始化缓存；
- `get(key)`: 如果关键字 `key` 存在于缓存中，返回其值并标记为「刚使用过」，否则返回 `-1`；
- `put(key, value)`: 如果已存在则更新值并标记为「刚使用过」；如果不存在则插入；若容量超出上限，则淘汰**最久未使用**的那个键。
要求：`get` 和 `put` 的平均时间复杂度必须都是 `O(1)`！

二、解法对比与复杂度
1. 解法一（手写「哈希表 + 双向链表」- 面试标准考察点）:
   - 为什么需要哈希表？为了 `O(1)` 查找 key 对应的节点。
   - 为什么需要**双向**链表（不能单链表）？为了把中间某个刚访问的节点 `O(1)` 从原位置摘掉并插到头部（摘节点需要知道它的前驱节点 `prev`）。
   - 技巧: 用 `head` 和 `tail` 两个哨兵假节点，避免判断头尾是否为空的边界麻烦！
   - 时间复杂度: get / put 均 O(1)
   - 空间复杂度: O(capacity)
2. 解法二（Python 标准库 OrderedDict 工程版）:
   - `OrderedDict` 底层本身就是双向链表 + 哈希表，`move_to_end(key)` 和 `popitem(last=False)` 直接搞定。

三、工程与 AI/大数据实战映射
- 高频真实场景: Redis 内存淘汰策略、FastAPI 热点结果缓存、RAG 向量检索高频 Query 缓存、大模型 Prompt / Embedding 本地缓存都离不开 LRU（Python 自带的 `@functools.lru_cache` 底层也是这套思想！）。
"""

from __future__ import annotations

from collections import OrderedDict


class _DNode:
    """双向链表节点。"""

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: _DNode | None = None
        self.next: _DNode | None = None


class LRUCacheManual:
    """解法一：手写双向链表 + 字典，面试手撕标准答案。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: dict[int, _DNode] = {}
        # 哨兵节点：head.next 是最久未使用的 (最旧)，tail.prev 是最近刚使用的 (最新)
        self.head = _DNode()
        self.tail = _DNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _DNode) -> None:
        """从双向链表中摘除一个已知节点，O(1)。"""
        assert node.prev is not None and node.next is not None
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append_to_tail(self, node: _DNode) -> None:
        """把节点插入到 tail 之前（标记为最近刚刚使用过），O(1)。"""
        last = self.tail.prev
        assert last is not None
        last.next = node
        node.prev = last
        node.next = self.tail
        self.tail.prev = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        # 访问后刷新热度：先从原位置摘下，再放到最新端
        self._remove(node)
        self._append_to_tail(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._remove(node)
            self._append_to_tail(node)
            return

        if len(self.cache) >= self.capacity:
            # 淘汰最久没用的：永远是 head.next
            oldest = self.head.next
            assert oldest is not None and oldest is not self.tail
            self._remove(oldest)
            del self.cache[oldest.key]

        new_node = _DNode(key, value)
        self.cache[key] = new_node
        self._append_to_tail(new_node)


class LRUCacheOrderedDict:
    """解法二：Python 标准库 OrderedDict 工程简洁版。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 弹出最左侧（最久未使用）的键


def run_tests() -> None:
    """自动化断言测试，模拟 LeetCode 官方交互序列。"""
    for cache_cls in (LRUCacheManual, LRUCacheOrderedDict):
        lru = cache_cls(2)
        lru.put(1, 1)
        lru.put(2, 2)
        assert lru.get(1) == 1  # 返回 1，此时 2 变成最久未使用
        lru.put(3, 3)  # 淘汰 key=2
        assert lru.get(2) == -1
        lru.put(4, 4)  # 淘汰 key=1
        assert lru.get(1) == -1
        assert lru.get(3) == 3
        assert lru.get(4) == 4
        # 测试更新已存在 key 的值与新鲜度
        lru.put(3, 30)
        assert lru.get(3) == 30
    print('✅ LeetCode 146 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 146. LRU 缓存 {'*' * 12}", sep='', end='\n\n')
    lru = LRUCacheManual(2)
    lru.put(1, 100)
    lru.put(2, 200)
    print(f'访问 key=1 -> {lru.get(1)}')
    lru.put(3, 300)
    print(f'插入 key=3 后访问被淘汰的 key=2 -> {lru.get(2)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
