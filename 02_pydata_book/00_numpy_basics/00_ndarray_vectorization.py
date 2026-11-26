"""
[主题]: NumPy 数组与向量化运算 (ndarray / broadcasting / 布尔索引)
[来源]: wesm/pydata-book 第 4 章「NumPy 基础」(本文件为自行重写的学习版)
[难度]: Easy
[前置知识]: 00_basic 语法主线、列表推导式、函数

一、主题说明
NumPy 的核心是 ndarray：同一类型、连续内存、支持整块运算。
数据分析快的秘密不是“写得巧”，而是把循环交给 C 语言实现的向量化运算。
广播(broadcasting)让形状不同的数组也能直接运算，而不用手动复制数据。

二、解法对比（以「把每个数平方后再筛出大于 10 的数」为例）
1. 直观版 square_filter_loop: Python for 循环逐个处理。
   - 时间复杂度 O(N)，但每一步都有 Python 解释器开销，慢且占内存。
2. 进阶版 square_filter_vectorized: 布尔索引 arr[arr * arr > 10]，整块计算。
   - 时间复杂度 O(N)，常数因子小很多，代码也更短。
3. 广播版 normalize_columns: 用 (N, 3) 数组减去 (3,) 的均值，无需循环也无需手动复制。
   - 时间复杂度 O(N * 3)，空间复杂度 O(N * 3)（生成新数组）

三、真实用途
- 大数据: Pandas、Spark 的 Pandas UDF、PyTorch 张量的底层思想都是向量化。
- 数据分析: 标准化、去均值、阈值筛选都是一行布尔索引完成。
- AI Agent / RAG: 向量检索的余弦相似度，就是对 (N, D) 矩阵做一次点积运算。
- 全栈开发: 图像缩放、报表统计等场景同样依赖数组运算。
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def square_filter_loop(values: list[int]) -> list[int]:
    """直观版：逐个平方，再用 if 筛选大于 10 的数。"""
    result: list[int] = []
    for value in values:  # 每个元素都要进入 Python 循环
        squared = value * value
        if squared > 10:
            result.append(squared)
    return result


def square_filter_vectorized(arr: NDArray[np.int64]) -> NDArray[np.int64]:
    """进阶版：整个数组一次性平方，布尔掩码直接筛选。"""
    squared = arr * arr  # 整块运算，不写循环
    return squared[squared > 10]  # 布尔索引：保留掩码为 True 的位置


def normalize_columns(matrix: NDArray[np.float64]) -> NDArray[np.float64]:
    """广播：每一列减去自己的均值。matrix.mean(axis=0) 的形状是 (列数,)，会自动广播到每一行。"""
    column_means = matrix.mean(axis=0)  # 形状 (3,)
    return matrix - column_means  # 形状 (N, 3) - (3,) -> (N, 3)


def run_tests() -> None:
    """自动化断言测试：覆盖常规用例与边界用例。"""
    data = [1, 2, 3, 4, 5]
    expected = [16, 25]  # 平方后: 1 4 9 16 25，只保留 > 10 的
    assert square_filter_loop(data) == expected
    assert square_filter_vectorized(np.array(data)).tolist() == expected

    # 边界：没有符合条件的元素时返回空数组 / 空列表
    assert square_filter_loop([0, 1]) == []
    assert square_filter_vectorized(np.array([0, 1])).size == 0

    # 广播：去均值后每列的均值应接近 0
    matrix = np.array([[1.0, 10.0, 100.0], [3.0, 20.0, 300.0]])
    centered = normalize_columns(matrix)
    assert centered.shape == (2, 3)  # 形状保持不变
    assert np.allclose(centered.mean(axis=0), 0.0)  # np.allclose 用于浮点数近似比较

    print('✅ NumPy 向量化所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} NumPy 数组与向量化 {'*' * 12}", sep='', end='\n\n')
    arr = np.arange(1, 8)  # [1 2 3 4 5 6 7]
    print('原始数组:', arr)
    print('向量化筛选结果:', square_filter_vectorized(arr))
    print('数组形状与类型:', arr.shape, arr.dtype)

    matrix = np.array([[1.0, 10.0], [3.0, 30.0]])
    print('广播去均值:\n', normalize_columns(matrix))
    run_tests()


if __name__ == '__main__':
    bootstrap()
