"""
[题目编号]: LeetCode 191. 位 1 的个数 (Number of 1 Bits)
[难度]: Easy
[所属专题]: 13_bit_and_math
[前置知识]: chapter03_sign (位运算不在语法主线，这里补充：& 与、>> 右移)、while 循环

一、题目描述
给定一个无符号整数 n，返回它的二进制表示中 1 的个数（也叫汉明重量 Hamming Weight）。
- 输入: n = 11 (二进制 1011) -> 输出 3
- 输入: n = 128 (二进制 10000000) -> 输出 1
- 输入: n = 2147483645 (二进制 1111...1101) -> 输出 30
- 边界: n = 0 -> 输出 0

二、解法对比
1. 解法一（直观版：逐位检查）:
   - 思路: 从最低位到最高位（共 32 位），每次用 (n >> i) & 1 取出第 i 位，是 1 就计数。
   - 时间复杂度: O(32)，即 O(1)（位数固定）
   - 空间复杂度: O(1)
2. 解法二（最优版：Brian Kernighan 算法）:
   - 思路: n & (n - 1) 会把 n 的最低位的 1 变成 0。循环做这件事，直到 n 变成 0，做了几次就有几个 1。
   - 时间复杂度: O(k)，k 为 1 的个数（只循环 1 的次数，而不是全部位数）
   - 空间复杂度: O(1)

三、工程与 AI/大数据实战映射
- **布隆过滤器 / 位图去重**: 海量用户 ID 去重时用一个 bit 表示“是否出现过”，统计已占位数要用到这里的汉明重量。
- **特征哈希与二进制特征**: 推荐、风控里的二值特征（是否点击、是否登录）常压缩成整数，计算命中数就是数 1。
- **网络与嵌入式**: 子网掩码、权限位（rwx）的解析都依赖位运算。
"""

from __future__ import annotations


def solve_bruteforce(n: int) -> int:
    """解法一：直观版，逐位检查 32 位，每位用右移加与运算取出。"""
    count = 0
    for i in range(32):  # 无符号 32 位整数，共 32 位
        if (n >> i) & 1:  # 右移 i 位后与 1 相与，结果为 1 说明第 i 位是 1
            count += 1
    return count


def solve_optimal(n: int) -> int:
    """解法二：Brian Kernighan 算法，每次消掉最低位的 1，循环次数等于 1 的个数。"""
    count = 0
    while n:  # n 变为 0 时结束
        n &= n - 1  # 消掉最低位的那个 1，例如 1100 & 1011 = 1000
        count += 1
    return count


def run_tests() -> None:
    """自动化断言测试：覆盖常规数字、2 的幂、全 1 与边界 0。"""
    cases = [
        (11, 3),  # 1011
        (128, 1),  # 10000000
        (2147483645, 30),  # 2^31 - 3：31 个 1 中去掉第 1 位，共 30 个 1
        (0, 0),  # 边界：没有任何 1
        (1, 1),  # 最小的正数
        ((1 << 32) - 1, 32),  # 全部 32 位都是 1
    ]
    for solver in (solve_bruteforce, solve_optimal):
        for value, expected in cases:
            assert solver(value) == expected, (solver.__name__, value)
    print('✅ 位 1 的个数所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode 191. 位 1 的个数 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例：11 的二进制是 1011，应该有 3 个 1
    sample = 11
    print(f'示例: n = {sample}，二进制 {bin(sample)}，结果 = {solve_optimal(sample)}')
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
