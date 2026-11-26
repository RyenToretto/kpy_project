# `kpy_project` 学习文件标准模板

## 1. 算法题 / 实战课 `.py` 模板

每个文件都必须能直接在 PyCharm 点击运行按钮，或通过 `.venv/bin/python <path>` 运行，并自动执行演示与 `assert` 自测。

```python
"""
[题目编号/主题]: LeetCode XX. 中文标题 (English Title)
[难度]: Easy / Medium / Hard
[所属专题]: 01_array_and_hashing
[前置知识]: 00_basic/chapter02_var (变量/类型) / 00_basic/chapter04_if_elif_else / for 循环 / dict

一、题目描述
用小白能看懂的语言复述题意与输入输出示例：
- 输入: ...
- 输出: ...
- 边界: 空列表、单元素、负数、重复元素等

二、解法对比与复杂度
1. 解法一（直观/暴力版）:
   - 思路: ...
   - 时间复杂度: O(...)
   - 空间复杂度: O(...)
2. 解法二（最优/面试标准版）:
   - 思路: ...
   - 时间复杂度: O(...)
   - 空间复杂度: O(...)

三、工程与 AI/大数据实战映射
说明该题思想在真实项目中的用处（如：哈希去重在日志清洗/RAG 文档去重中的作用、Top-K 堆在检索重排中的作用、DAG 拓扑排序在 AI Agent 工作流编排中的作用）。
"""

from __future__ import annotations


def solve_bruteforce(...) -> ...:
    """解法一：直观入门版，每一步带中文注释，帮助建立思维路径。"""
    ...


def solve_optimal(...) -> ...:
    """解法二：最优解 / 面试标准版，追求时间或空间最优。"""
    ...


def run_tests() -> None:
    """自动化测试：覆盖常规用例与边界用例。"""
    for solver in (solve_bruteforce, solve_optimal):
        assert solver(...) == ...
    print('✅ 所有测试用例通过！')


def bootstrap() -> None:
    print(f"\n\n{'*' * 12} LeetCode XX. 标题 {'*' * 12}", sep='', end='\n\n')
    # 1. 运行示例并打印直观过程
    sample_result = solve_optimal(...)
    print(f'示例输出: {sample_result}')
    # 2. 执行自动断言校验
    run_tests()


if __name__ == '__main__':
    bootstrap()
```

## 2. 专题 `README.md` 模板

```markdown
# XX_topic_name | 专题中文名

- **学习阶段**: 第 X 阶段
- **前置语法**: `chapter0X_xxx`
- **为什么学它（通向大数据 / AI / 全栈）**: 1~2 句话说明实际价值

## 核心心法（一句话 + 代码模板）
简短列出本专题最常用的 1~2 个 Python 套路模板。

## 顺序刷题清单（从易到难，`00_` 编号）
| 编号 | 题号与名称 | 难度 | 核心技巧 | 本地文件 | 状态 |
| --- | --- | --- | --- | --- | --- |
| `00_` | ... | Easy | ... | `00_lcXXXX_xxx.py` | ✅ / 📝 待生成 |
```

## 3. 兄弟学习仓库 `00_xxx` 模块模板

当把外部 GitHub 开源项目（如 `00_pydata_book`、`00_all_in_rag`、`00_hello_agents`）纳入本仓库时：
- 目录统一放在仓库根目录：`NN_<repo_slug>/`，`NN` 为学习路线中的阶段编号（`00_leetcode` 为第一阶段，之后 `01_`、`02_` ... 递增）。
- 顶层放置 `README.md`（记录原仓库链接、学习目标、环境依赖、章节映射）
- 子目录与脚本从 `00_` 开始顺序编号：`00_setup/` -> `01_xxx/` -> `02_xxx/`，每个独立 `.py` 依然保留 `Docstring` + 中文注释 + `run_tests()` + `bootstrap()`。
