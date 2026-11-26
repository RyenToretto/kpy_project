"""
[题目编号]: LeetCode 33. 搜索旋转排序数组 (Search in Rotated Sorted Array)
[难度]: Medium (二分进阶必考)
[所属专题]: 05_binary_search
[前置知识]: LeetCode 704 二分查找模板

一、题目描述
升序数组 `nums` 在某个未知下标处进行了旋转（例如 `[0,1,2,4,5,6,7]` 变为 `[4,5,6,7,0,1,2]`），数组中**无重复元素**。
给定目标值 `target`，如果存在返回下标，否则返回 `-1`，要求时间复杂度 `O(log n)`。

示例:
- 输入: nums = [4, 5, 6, 7, 0, 1, 2], target = 0 -> 输出: 4
- 输入: nums = [4, 5, 6, 7, 0, 1, 2], target = 3 -> 输出: -1
- 边界: [1], target=0 -> -1；[3, 1], target=1 -> 1

二、解法与复杂度
- 思路（局部有序性判断：每次一刀切下去，左右两半至少有一半是完全有序的！）:
  - 计算 `mid` 后：
    - 若 `nums[left] <= nums[mid]`：说明**左半边 `[left, mid]` 严格有序**！
      - 若 `nums[left] <= target < nums[mid]`：target 肯定落在有序的左半边，缩右边界 `right = mid - 1`；
      - 否则只能去右半边 `left = mid + 1`。
    - 否则（`nums[left] > nums[mid]`）：说明**右半边 `[mid, right]` 严格有序**！
      - 若 `nums[mid] < target <= nums[right]`：target 肯定落在有序的右半边，缩左边界 `left = mid + 1`；
      - 否则去左半边 `right = mid - 1`。
- 时间复杂度: O(log n)
- 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- 环形日志 / 分片滚动索引查询: 在循环覆盖写日志（Ring Buffer）或按时间切分但首尾衔接的分片文件里二分检索时间戳，用的正是同一思想。
"""

from __future__ import annotations


def search_rotated(nums: list[int], target: int) -> int:
    """判断哪一侧有序，再利用有序侧的范围决定收缩方向。"""
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid

        # 左半边 [left, mid] 是有序的（注意 <= 处理 left == mid 的情况）
        if nums[left] <= nums[mid]:
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # 否则右半边 [mid, right] 一定是有序的
        else:
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


def run_tests() -> None:
    """自动化断言测试。"""
    cases = [
        ([4, 5, 6, 7, 0, 1, 2], 0, 4),
        ([4, 5, 6, 7, 0, 1, 2], 3, -1),
        ([1], 0, -1),
        ([1], 1, 0),
        ([3, 1], 1, 1),
        ([5, 1, 3], 5, 0),
    ]
    for nums, target, expected in cases:
        assert search_rotated(nums, target) == expected, f'失败: {nums}, {target}'
    print('✅ LeetCode 33 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 33. 搜索旋转排序数组 {'*' * 12}", sep='', end='\n\n')
    nums = [4, 5, 6, 7, 0, 1, 2]
    print(f'在 {nums} 中搜索 0 的位置: {search_rotated(nums, 0)}')
    run_tests()


if __name__ == '__main__':
    bootstrap()
