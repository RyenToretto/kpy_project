"""
[题目编号]: LeetCode 239. 滑动窗口最大值 (Sliding Window Maximum / 单调队列)
[难度]: Hard (单调双端队列第一代表题，参考 kamyu104 15 行 deque 思路重写为 Python 3.12 教学版)
[所属专题]: 14_hard_capstones
[前置知识]: collections.deque、03_sliding_window (滑动窗口)、04_stack_and_queue (单调栈思想)

一、题目描述
给你一个整数数组 `nums`，有一个大小为 `k` 的滑动窗口从数组的最左侧移动到数组的最右侧。
你只可以看到在滑动窗口内的 `k` 个数字，滑动窗口每次只向右移动一位。返回每一步滑动窗口中的最大值。

示例:
- 输入: nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3 -> 输出: [3, 3, 5, 5, 6, 7]
- 输入: nums = [1], k = 1 -> 输出: [1]
- 边界: 全递减 [5, 4, 3, 2, 1], k = 3 -> [5, 4, 3]；k == len(nums) -> [max(nums)]

二、解法对比与复杂度
1. 解法一（每次窗口切片直接求 `max`）:
   - 时间复杂度: O(n * k)，当 n=10万、k=5万 时会做 50 亿次比较超时。
   - 空间复杂度: O(1)（不算结果）
2. 解法二（单调递减双端队列 `deque` 存下标 - 真正 O(n) 最优解）:
   - 核心直觉（「比你年轻还比你强，你就永远没机会出头了」）：
     队列里存放**可能是未来窗口最大值**的下标，且对应数值严格从队头到队尾**递减**：
     1. **队尾淘汰**：新元素 `nums[i]` 来之前，把队尾所有 `<= nums[i]` 的下标全部踢出（它们既比 `i` 早过期，值还不如 `i` 大，永远不可能当最大值）。
     2. **队头过期**：如果队头下标 `dq[0] <= i - k`（已经滑出当前窗口左边界 `[i-k+1, i]`），从队头踢出。
     3. **取结果**：只要 `i >= k - 1`（窗口已经攒够 k 个元素），队头 `nums[dq[0]]` 就是当前窗口最大值！
   - 时间复杂度: O(n)，每个下标最多入队一次、出队一次。
   - 空间复杂度: O(k)

三、工程与 AI/大数据实战映射
- **Flink / 实时流计算滑窗极值 (Sliding Window Max/Min)**: 在实时监控最近 5 分钟接口延迟峰值、异常流量尖刺检测、量化 K 线窗口极值跟踪时，单调队列是把每窗口 O(k) 降到 O(1) 均摊耗时的标准算法。
"""

from __future__ import annotations

from collections import deque


def max_sliding_window_bruteforce(nums: list[int], k: int) -> list[int]:
    """解法一：每次切片求 max，时间 O(n * k)，只适合小数据验证。"""
    if not nums or k <= 0:
        return []
    return [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]


def max_sliding_window_deque(nums: list[int], k: int) -> list[int]:
    """解法二：单调递减双端队列（存下标），时间复杂度 O(n)，空间 O(k)。"""
    if not nums or k <= 0:
        return []

    dq: deque[int] = deque()  # 队头永远是当前窗口最大值的下标
    result: list[int] = []

    for i, num in enumerate(nums):
        # 1. 队头已经滑出窗口左边界（合法窗口起点是 i - k + 1），移除过期下标
        if dq and dq[0] <= i - k:
            dq.popleft()

        # 2. 维护单调递减性：队尾不如当前数大的老元素全部出队
        while dq and nums[dq[-1]] <= num:
            dq.pop()

        dq.append(i)

        # 3. 窗口形成后（下标到达 k - 1 起），队头即当前窗口最大值
        if i >= k - 1:
            result.append(nums[dq[0]])

    return result


def run_tests() -> None:
    """自动化断言测试，含全递增、全递减、重复值与 k=1 / k=n 边界。"""
    cases = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3, [3, 3, 5, 5, 6, 7]),
        ([1], 1, [1]),
        ([5, 4, 3, 2, 1], 3, [5, 4, 3]),
        ([1, 2, 3, 4, 5], 3, [3, 4, 5]),
        ([2, 2, 2, 2], 2, [2, 2, 2]),
        ([9, 11], 2, [11]),
        ([], 3, []),
    ]
    for solver in (max_sliding_window_bruteforce, max_sliding_window_deque):
        for nums, k, expected in cases:
            actual = solver(nums, k)
            assert actual == expected, f'{solver.__name__} 失败: {nums}, k={k} -> {actual}'
    print('✅ LeetCode 239 (单调队列滑窗最大值) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 239. 滑动窗口最大值 (单调队列) {'*' * 12}", sep='', end='\n\n')
    sample = [1, 3, -1, -3, 5, 3, 6, 7]
    print(f'序列 {sample}, k=3 -> 滑窗最大值: {max_sliding_window_deque(sample, 3)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
