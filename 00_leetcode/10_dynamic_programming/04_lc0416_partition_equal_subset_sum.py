"""
[题目编号]: LeetCode 416. 分割等和子集 (Partition Equal Subset Sum / 0-1 背包标准第一题)
[难度]: Medium (补齐 0-1 背包模型必刷题，与 01_lc0322 完全背包正序遍历形成对比)
[所属专题]: 10_dynamic_programming
[前置知识]: 10_dynamic_programming/01_lc0322_coin_change (完全背包正序)、奇偶性判断

一、题目描述
给你一个只包含正整数的非空数组 `nums`。请你判断是否可以将这个数组分割成两个子集，使得两个子集的元素和相等。

示例:
- 输入: nums = [1, 5, 11, 5] -> 输出: True ([1, 5, 5] 和 [11])
- 输入: nums = [1, 2, 3, 5] -> 输出: False (总和 11 为奇数，不可能平分)
- 边界: [1] -> False；[2, 2, 1, 1] -> True；[1, 2, 5] -> False

二、解法对比与复杂度（动规五部曲 + 为什么 0-1 背包必须倒序！）
问题转化：总和为 `total`；如果 `total` 是奇数直接 `False`。否则只需回答：**能否从 `nums` 里挑出若干个数（每个数最多用一次），恰好凑出背包容量 `target = total // 2`？**

1. 解法一（记忆化搜索 DFS(idx, remaining) - 最直白思考路径）:
   - 思路: 对第 `idx` 个数做二选一：「选它」或「不选它」，并用 `@lru_cache` 缓存避免重复分支。
   - 时间复杂度: O(n * target)
   - 空间复杂度: O(n * target)
2. 解法二（0-1 背包一维滚动数组 `dp` - 倒序遍历容量核心模板）:
   - **动规五部曲**：
     1. `dp[j]` 含义：能否凑出总和为 `j`（`bool` 型；或者用整数表示容量 `j` 最多能装多大重量，`dp[j] == j` 时成功）。
     2. 递推公式：`dp[j] = dp[j] or dp[j - num]`。
     3. 初始化：`dp[0] = True`（什么都不选，总和为 0 一定可以），其余 `False`。
     4. **遍历顺序（灵魂考点！对比 LC 322 完全背包）**：
        - 外层遍历物品 `num`；内层必须**倒序遍历容量 `range(target, num - 1, -1)`**！
        - **为什么必须倒序**？如果正序从左到右更新，刚写入的 `dp[j - num]` 可能已经在本轮用过当前数字 `num` 了，等价于「同一个数字被拿了多次」（那就变成完全背包了！）。倒序更新时，`dp[j - num]` 一定还是上一轮没放过 `num` 的旧状态！
   - 时间复杂度: O(n * target)
   - 空间复杂度: O(target)

三、工程与 AI/大数据实战映射
- **双机负载均衡 / 分片均衡拆分**: 把一批不同耗时或不同大小的任务/数据分片平均拆成总负载尽可能相等的两组并行执行（如双 GPU 卡均衡切分模型层或批数据）。
"""

from __future__ import annotations

from functools import lru_cache


def can_partition_memo(nums: list[int]) -> bool:
    """解法一：记忆化递归 DFS，枚举每个元素选与不选。"""
    total = sum(nums)
    if total % 2 == 1:
        return False
    target = total // 2

    @lru_cache(maxsize=None)
    def dfs(idx: int, remaining: int) -> bool:
        if remaining == 0:
            return True
        if idx >= len(nums) or remaining < 0:
            return False
        # 选 nums[idx] 或跳过 nums[idx]
        return dfs(idx + 1, remaining - nums[idx]) or dfs(idx + 1, remaining)

    return dfs(0, target)


def can_partition_knapsack(nums: list[int]) -> bool:
    """解法二：0-1 背包一维滚动数组（布尔值版），内层倒序遍历防止重复使用同一元素。"""
    total = sum(nums)
    if total % 2 == 1:
        return False
    target = total // 2

    # 快速剪枝：只要最大元素已经超过一半，剩下所有元素加起来都不够一半
    if max(nums, default=0) > target:
        return False

    dp = [False] * (target + 1)
    dp[0] = True

    for num in nums:
        # 关键：必须从大到小倒序遍历！这样 dp[s - num] 读取的是“未放当前 num 前”的状态
        for s in range(target, num - 1, -1):
            if dp[s - num]:
                dp[s] = True
        if dp[target]:
            return True  # 提前达成目标可直接结束

    return dp[target]


def run_tests() -> None:
    """自动化断言测试，特别覆盖“同一数字不能用两次”的 0-1 背包陷阱用例。"""
    cases = [
        ([1, 5, 11, 5], True),
        ([1, 2, 3, 5], False),
        ([1, 2, 5], False),  # 如果误写成正序遍历（把 1 用多次）会错判成 True！
        ([2, 2, 1, 1], True),
        ([100], False),
        ([1, 1], True),
        ([3, 3, 3, 4, 5], True),  # [3, 3, 3] = 9, [4, 5] = 9
    ]
    for solver in (can_partition_memo, can_partition_knapsack):
        for nums, expected in cases:
            actual = solver(nums)
            assert actual is expected, f'{solver.__name__} 失败: {nums} -> {actual}'
    print('✅ LeetCode 416 (0-1 背包分割等和子集) 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 416. 分割等和子集 (0-1 背包) {'*' * 12}", sep='', end='\n\n')
    sample = [1, 5, 11, 5]
    print(f'数组 {sample} 能否平分成和相等的两组: {can_partition_knapsack(sample)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
