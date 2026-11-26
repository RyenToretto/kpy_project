"""
[题目编号]: LeetCode 875. 爱吃香蕉的珂珂 (Koko Eating Bananas)
[难度]: Medium (「二分答案」第一标准模板题，参考 kamyu104 思路重写为 Python 3.12 教学版)
[所属专题]: 05_binary_search
[前置知识]: 05_binary_search/00_lc0704_binary_search (二分左右边界)、整除向上取整 `(x + k - 1) // k`

一、题目描述
有 `n` 堆香蕉，第 `i` 堆中有 `piles[i]` 根香蕉。警卫将在 `h` 小时后回来。
珂珂决定她吃香蕉的速度 `k`（根/小时）。每个小时她选择一堆吃掉 `k` 根；如果这堆少于 `k` 根，她吃完这堆后这一小时内**不再吃别的堆**。
求她在 `h` 小时内吃掉所有香蕉的**最小速度 `k`**（`k` 为正整数）。

示例:
- 输入: piles = [3, 6, 7, 11], h = 8 -> 输出: 4
- 输入: piles = [30, 11, 23, 4, 20], h = 5 -> 输出: 30
- 输入: piles = [30, 11, 23, 4, 20], h = 6 -> 输出: 23

二、解法对比与复杂度
为什么能用二分？这题不是在输入数组里找数，而是在**「答案空间」 `[1, max(piles)]` 里二分**！
因为速度 `k` 越大，所需总时间越短（满足单调性）：一旦某个速度 `k` 能在 `h` 小时内吃完，所有更大的速度也一定可以；我们要找的是「满足条件的最左边界」。
1. 解法一（线性枚举速度 1, 2, 3... 直到可行）:
   - 时间复杂度: O(n * max(piles))，单堆很大（如 10^9）必超时。
   - 空间复杂度: O(1)
2. 解法二（答案单调二分 - Binary Search on Answer 核心套路）:
   - 思路:
     1. 确定答案下界 `left = 1`、上界 `right = max(piles)`（速度再大每堆也只需 1 小时，不会更快）。
     2. 编写单调判定函数 `can_finish(speed)`：每堆耗时 `(pile + speed - 1) // speed`（整数向上取整，避免浮点精度误差），求和判断是否 `<= h`。
     3. 如果 `can_finish(mid)` 成立，说明 `mid` 可行，但可能还有更小的速度，收缩右边界 `right = mid - 1`；否则太慢了，提高速度 `left = mid + 1`。
   - 时间复杂度: O(n log(max(piles)))
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- **容量规划 / 限流与批处理并发寻优**: 如「保证所有任务在 SLA（如 8 小时）内跑完的最小并发 Worker 数 / 最小 GPU 批大小」「RAG 离线建索引的最低限流 QPS」，凡是「求满足约束的最小/最大资源配置」且具备单调性，全是**二分答案**！
"""

from __future__ import annotations


def min_eating_speed_linear(piles: list[int], h: int) -> int:
    """解法一：从 1 开始线性试探，适合理解题意，大数值下会慢。"""
    max_pile = max(piles)
    for speed in range(1, max_pile + 1):
        hours = sum((pile + speed - 1) // speed for pile in piles)
        if hours <= h:
            return speed
    return max_pile


def min_eating_speed_binary_search(piles: list[int], h: int) -> int:
    """解法二：在答案区间 [1, max(piles)] 上做左边界二分查找。"""
    def can_finish(speed: int) -> bool:
        hours_needed = 0
        for pile in piles:
            # 整数向上取整：等价于 math.ceil(pile / speed)，但全整数计算没有浮点误差
            hours_needed += (pile + speed - 1) // speed
            if hours_needed > h:
                return False  # 提前剪枝，没必要把剩下堆全部算完
        return True

    left, right = 1, max(piles)
    ans = right

    while left <= right:
        mid = left + (right - left) // 2
        if can_finish(mid):
            ans = mid
            right = mid - 1  # mid 可行，继续向左试探有没有更小的速度
        else:
            left = mid + 1   # mid 太慢，必须提速

    return ans


def run_tests() -> None:
    """自动化断言测试，含普通案例、时间紧迫极值和大数测试。"""
    small_cases = [
        ([3, 6, 7, 11], 8, 4),
        ([30, 11, 23, 4, 20], 5, 30),
        ([30, 11, 23, 4, 20], 6, 23),
        ([1], 1, 1),
        ([10], 100, 1),
    ]
    for solver in (min_eating_speed_linear, min_eating_speed_binary_search):
        for piles, h, expected in small_cases:
            assert solver(piles, h) == expected, f'{solver.__name__} 失败: {piles}, h={h}'

    # 大数边界测试（线性版会极慢，二分秒出结果）：1 堆 10^9 根，10^9 小时 -> 速度 1；1 小时 -> 10^9
    assert min_eating_speed_binary_search([10**9], 10**9) == 1
    assert min_eating_speed_binary_search([10**9], 1) == 10**9
    print('✅ LeetCode 875 (二分答案) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 875. 爱吃香蕉的珂珂 (二分答案) {'*' * 12}", sep='', end='\n\n')
    piles, h = [3, 6, 7, 11], 8
    print(f'香蕉堆 {piles}, 限期 {h} 小时 -> 最小速度: {min_eating_speed_binary_search(piles, h)} 根/小时')
    run_tests()


if __name__ == '__main__':
    bootstrap()
