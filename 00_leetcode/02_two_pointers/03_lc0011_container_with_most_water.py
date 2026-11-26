"""
[题目编号]: LeetCode 11. 盛最多水的容器 (Container With Most Water)
[难度]: Medium
[所属专题]: 02_two_pointers
[前置知识]: for 循环嵌套、while 循环、min 与 max 函数、列表下标

一、题目描述
给定长度为 n 的整数数组 height，第 i 条竖线的两端坐标是 (i, 0) 和 (i, height[i])。
选择两条竖线，与 x 轴共同构成一个容器，求能容纳水的最大面积。
- 面积 = min(左边高度, 右边高度) × 两线的水平距离
- 输入: height = [1, 8, 6, 2, 5, 4, 8, 3, 7] -> 输出 49（下标 1 与 8，min(8,7) × 7）
- 输入: height = [1, 1] -> 输出 1
- 边界: 至少有 2 条竖线

二、解法对比
1. 解法一（直观版：枚举所有两两组合）:
   - 思路: 双重循环取出每一对 (i, j)，计算面积并记录最大值。
   - 时间复杂度: O(n^2)
   - 空间复杂度: O(1)
2. 解法二（最优版：左右双指针）:
   - 思路: 左指针从最左、右指针从最右出发。面积由“短板”决定，所以每次移动较短的那一侧：
     如果保留短板，宽度只会变小，面积不可能变大，因此只能舍弃短板。
   - 时间复杂度: O(n)，每个指针最多移动 n 次
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- **木桶原理 / 瓶颈分析**: 系统吞吐往往由最慢的环节决定（短板），优化时要先找瓶颈，这正是“每次移动短板”的思想。
- **数据分析 / 双指针对齐**: 两个有序时间序列做区间匹配时，同样用双指针沿较早结束的一侧推进。
- **AI Agent / RAG**: 在两个候选集中找组合最优解（如两段文本拼接的得分）时，双指针能把组合数从平方降到线性。
"""

from __future__ import annotations


def solve_bruteforce(height: list[int]) -> int:
    """解法一：枚举所有两条竖线的组合，计算面积并取最大值。"""
    best = 0
    n = len(height)
    for i in range(n):  # 左边的线
        for j in range(i + 1, n):  # 右边的线
            area = min(height[i], height[j]) * (j - i)  # 短板高度 × 宽度
            best = max(best, area)
    return best


def solve_optimal(height: list[int]) -> int:
    """解法二：左右双指针，每次舍弃较短的一侧。"""
    left, right = 0, len(height) - 1  # 两端出发
    best = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)  # 当前容器的面积
        best = max(best, area)
        # 短板决定面积，移动短板才有机会变大；长板保留没有损失
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return best


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例、等高、单调与边界。"""
    cases = [
        ([1, 8, 6, 2, 5, 4, 8, 3, 7], 49),
        ([1, 1], 1),
        ([4, 3, 2, 1, 4], 16),  # 两端都是 4，宽度 4，面积 16
        ([1, 2, 1], 2),
        ([2, 3, 4, 5, 18, 17, 6], 17),  # 单峰与递增组合
        ([5, 5, 5, 5], 15),  # 全部等高时，最远两端面积最大
    ]
    for solver in (solve_bruteforce, solve_optimal):
        for height, expected in cases:
            assert solver(height) == expected, (solver.__name__, height)
    print('✅ 盛最多水的容器所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 11. 盛最多水的容器 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例
    sample = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    print(f'示例: height = {sample}，最大面积 = {solve_optimal(sample)}')
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
