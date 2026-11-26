"""
[题目编号]: LeetCode 460. LFU 缓存 (LFU Cache)
[难度]: Hard (比 LRU 更进一层的系统设计经典题，参考 kamyu104 频率桶 OrderedDict 思路重写为 Python 3.12 教学版)
[所属专题]: 06_linked_list
[前置知识]: 06_linked_list/01_lc0146_lru_cache (LRU 缓存)、OrderedDict、defaultdict

一、题目描述
请你为「最不经常使用 (Least Frequently Used, LFU)」缓存算法设计并实现数据结构：
- `LFUCache(capacity)`: 初始化缓存容量（注意边界：`capacity == 0` 时所有 `put` 都不存，`get` 永远返回 `-1`）。
- `get(key)`: 若存在则返回值，并使该键的访问频次 `+1`；否则返回 `-1`。
- `put(key, value)`: 若键存在则更新值且频次 `+1`；若不存在则插入（初始频次为 `1`）。若容量已满，优先淘汰**访问频次最低**的键；如果有多条频次并列最低，则淘汰其中**最久未使用**的那一条（退化成 LRU 规则）！
要求：`get` 和 `put` 的平均时间复杂度必须为 `O(1)`。

二、解法对比与复杂度
1. 解法一（按频次排序/小顶堆淘汰）:
   - 思路: 每次淘汰时扫一遍或用堆找最小频次。查找容易但修改中间元素频次要 `O(log n)` 或 `O(n)`。
2. 解法二（双哈希 + 频率桶 OrderedDict - 严格 O(1) 最优设计）:
   - 思路: 维护三样东西即可实现 O(1)：
     1. `key_to_val_freq`: `key -> (value, freq)`，O(1) 查值和当前频次。
     2. `freq_buckets`: `freq -> OrderedDict[key, None]`。**每个频次对应一个 LRU 桶**！同频次的键谁最久没用，就自然排在 `OrderedDict` 最左边，可以直接 `popitem(last=False)` O(1) 弹出！
     3. `min_freq`: 实时记录当前全局最小频次。
   - **最妙的不变量 (`min_freq` 怎么更新？)**：
     - 当某个旧键从 `freq` 升到 `freq + 1` 时：把它从 `freq` 桶移走；如果原来 `freq == min_freq` 且该桶空了，则 `min_freq += 1`。
     - 当插入一个全新键时：它的初始频次一定是 `1`，所以 `min_freq` 直接重置为 `1`！
   - 时间复杂度: `get` / `put` 均 O(1)
   - 空间复杂度: O(capacity)

三、工程与 AI/大数据实战映射
- **热点词典 / CDN / RAG 热门文档缓存**: 单靠 LRU 容易被一次性的全表扫描把缓存全部冲刷掉（缓存污染）；LFU 能保留真正高频命中的热点知识块和权重分片（如 Redis 的 `allkeys-lfu` 策略）。
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict


class LFUCacheNaive:
    """直观对照版：每次淘汰扫描找 (最小频次, 最早时间戳)，时间 O(n)，用于验证逻辑正确性。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.tick = 0
        self.store: dict[int, list[int]] = {}  # key -> [val, freq, last_used_tick]

    def get(self, key: int) -> int:
        if key not in self.store:
            return -1
        self.tick += 1
        self.store[key][1] += 1
        self.store[key][2] = self.tick
        return self.store[key][0]

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return
        self.tick += 1
        if key in self.store:
            self.store[key][0] = value
            self.store[key][1] += 1
            self.store[key][2] = self.tick
            return
        if len(self.store) >= self.capacity:
            victim = min(self.store, key=lambda k: (self.store[k][1], self.store[k][2]))
            del self.store[victim]
        self.store[key] = [value, 1, self.tick]


class LFUCache:
    """进阶最优版：双哈希 + 频率桶 OrderedDict，get/put 均摊 O(1)。"""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.min_freq = 0
        self.key_to_val_freq: dict[int, tuple[int, int]] = {}
        self.freq_buckets: dict[int, OrderedDict[int, None]] = defaultdict(OrderedDict)

    def _touch(self, key: int, new_val: int | None = None) -> int:
        """内部公共操作：让已存在的 key 频次 +1，并在对应频率桶间 O(1) 迁移。"""
        val, freq = self.key_to_val_freq[key]
        if new_val is not None:
            val = new_val

        # 1. 从旧频次桶里移除
        old_bucket = self.freq_buckets[freq]
        del old_bucket[key]
        if not old_bucket:
            del self.freq_buckets[freq]
            if self.min_freq == freq:
                self.min_freq += 1  # 最小频次正好只有一个元素且升级了，min_freq 随之上移

        # 2. 加入新频次桶末尾（代表该频次内最新使用）
        next_freq = freq + 1
        self.freq_buckets[next_freq][key] = None
        self.key_to_val_freq[key] = (val, next_freq)
        return val

    def get(self, key: int) -> int:
        if key not in self.key_to_val_freq:
            return -1
        return self._touch(key)

    def put(self, key: int, value: int) -> None:
        if self.capacity <= 0:
            return

        if key in self.key_to_val_freq:
            self._touch(key, new_val=value)
            return

        if len(self.key_to_val_freq) >= self.capacity:
            # 找到最小频次桶中最左侧（最久未使用）的 key 淘汰
            lfu_bucket = self.freq_buckets[self.min_freq]
            evict_key, _ = lfu_bucket.popitem(last=False)
            if not lfu_bucket:
                del self.freq_buckets[self.min_freq]
            del self.key_to_val_freq[evict_key]

        # 新插入的键初始频次必定是 1，最小频次同步重置为 1
        self.key_to_val_freq[key] = (value, 1)
        self.freq_buckets[1][key] = None
        self.min_freq = 1


def run_tests() -> None:
    """自动化断言测试：包含官方序列、容量 0 边界与同频次 LRU 平局淘汰测试。"""
    for cache_cls in (LFUCacheNaive, LFUCache):
        # 1. 标准 LFU 交互序列
        lfu = cache_cls(2)
        lfu.put(1, 1)
        lfu.put(2, 2)
        assert lfu.get(1) == 1      # 频次: key1=2, key2=1
        lfu.put(3, 3)               # 淘汰最低频 key2；当前 key1=2, key3=1
        assert lfu.get(2) == -1
        assert lfu.get(3) == 3      # 频次: key1=2, key3=2（3 比 1 更近使用）
        lfu.put(4, 4)               # 频次并列为 2，淘汰最久未用的 key1！
        assert lfu.get(1) == -1
        assert lfu.get(3) == 3
        assert lfu.get(4) == 4

        # 2. 容量为 0 边界
        zero_cache = cache_cls(0)
        zero_cache.put(1, 10)
        assert zero_cache.get(1) == -1

        # 3. 覆盖更新已存在 key 的值并增加频次
        c = cache_cls(2)
        c.put(1, 10)
        c.put(2, 20)
        c.put(1, 100)  # key1 频次变 2，值变 100
        c.put(3, 30)   # 淘汰 key2
        assert c.get(1) == 100
        assert c.get(2) == -1
        assert c.get(3) == 30

    print('✅ LeetCode 460 (LFU 缓存) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 460. LFU 缓存 {'*' * 12}", sep='', end='\n\n')
    lfu = LFUCache(2)
    lfu.put(1, 10)
    lfu.put(2, 20)
    print(f'访问热点 key=1 (频次升为 2) -> {lfu.get(1)}')
    lfu.put(3, 30)
    print(f'容量满插入 key=3 后，低频 key=2 被淘汰 -> get(2)={lfu.get(2)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
