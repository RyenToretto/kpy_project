# kpy_project

Python 3.12 从零到精通的个人学习仓库。语法按 `00_basic/chapter01` 起顺序推进；算法与各学习仓库放在根目录，**按学习阶段递增编号**：第一阶段是 `00_leetcode`，之后依次 `01_`、`02_` ...，按编号从小到大学。

## 目录

| 路径 | 阶段 | 内容 |
| --- | --- | --- |
| `00_basic/chapter01_hello/` ~ `00_basic/chapter05_match/` | 语法主线 | 输出、变量、运算符、分支、`match` |
| `00_interview/` | 练习 | 面试向小练习（高斯求和、闰年） |
| [`00_leetcode/`](./00_leetcode/README.md) | 阶段 1 | 算法训练营，**总题数 41**（已完成 35，待生成 6） |
| [`01_python_100_days/`](./01_python_100_days/README.md) | 阶段 2 | Python-100-Days 中文路线 |
| [`02_pydata_book/`](./02_pydata_book/README.md) | 阶段 2 | 《利用 Python 进行数据分析》 |
| [`03_llm_universe/`](./03_llm_universe/README.md) | 阶段 3 | 大模型应用开发入门 |
| [`04_all_in_rag/`](./04_all_in_rag/README.md) | 阶段 3 | RAG 技术全栈 |
| [`05_hello_agents/`](./05_hello_agents/README.md) | 阶段 4 | 从零构建智能体 |
| [`06_mcp_beginners/`](./06_mcp_beginners/README.md) | 阶段 4 | MCP 入门 |
| [`07_genai_agents/`](./07_genai_agents/README.md) | 阶段 4 | 生成式 AI 智能体案例 |
| [`08_ai_fullstack_fastapi/`](./08_ai_fullstack_fastapi/README.md) | 阶段 5 | FastAPI 全栈与认证 |
| [`09_happy_llm/`](./09_happy_llm/README.md) | 阶段 6 | 从零开始构建大模型（Transformer 原理） |
| [`10_llms_from_scratch/`](./10_llms_from_scratch/README.md) | 阶段 6 | 从零手写类 GPT 模型 |
| [`11_rag_techniques/`](./11_rag_techniques/README.md) | 阶段 6 | RAG 进阶技巧 |

## 一、可加入的学习仓库（推荐度从高到低）

下表按**推荐度**从高到低排列，目录编号按**学习顺序**分配。推荐度不等于学习顺序，学习顺序以下面的「阶段路线」为准。

| 排名 | 推荐度 | GitHub 仓库 | 目录（学习编号） | 适合阶段与核心内容 | 与目标的匹配度 |
| --- | --- | --- | --- | --- | --- |
| 1 | ⭐⭐⭐⭐⭐+ | [datawhalechina/hello-agents](https://github.com/datawhalechina/hello-agents) | `05_hello_agents` | 《从零开始构建智能体》：ReAct/Reflection 手写、LangGraph、MCP/A2A、记忆/上下文工程、多智能体与毕业实战 | 当前最推荐的主线实战课：手写 Agent 框架、主流框架、MCP 与综合项目一次打通。 |
| 2 | ⭐⭐⭐⭐⭐ | [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) | `08_ai_fullstack_fastapi` | 官方 FastAPI + React + SQLModel + PostgreSQL + Docker + JWT + Pytest 全栈模板 | 自由职业/副业与 AI 全栈底座：把大模型/RAG/Agent 包装成带登录、数据库的完整 Web 产品。 |
| 3 | ⭐⭐⭐⭐⭐ | [datawhalechina/all-in-rag](https://github.com/datawhalechina/all-in-rag) | `04_all_in_rag` | 从数据清洗、多模态 Embedding、Milvus 向量库、Text2SQL 到生产级 RAG 项目实战 | 贴近企业真实 RAG 全栈工程，把向量库、混合检索、Text2SQL 与评测串成可上线作品。 |
| 4 | ⭐⭐⭐⭐⭐ | [NirDiamant/GenAI_Agents](https://github.com/NirDiamant/GenAI_Agents) | `07_genai_agents` | 50+ 生成式 AI 智能体实战案例（简单对话 -> 工具调用 -> 多智能体协作） | 案例贴近真实需求（客服、研报分析、自动化办公），适合拆成个人作品集与外包模板。 |
| 5 | ⭐⭐⭐⭐⭐ | [rasbt/LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch) | `10_llms_from_scratch` | PyTorch 从零手写一个类 GPT 大模型（分词器 -> 注意力 -> 预训练 -> 指令微调） | 公认代码最干净的 LLM 底层仓库，用来从只会调包转到真正看懂模型机理。 |
| 6 | ⭐⭐⭐⭐☆ | [datawhalechina/happy-llm](https://github.com/datawhalechina/happy-llm) | `09_happy_llm` | 中文系统性大模型教材：Transformer -> 手写 LLaMA2 -> SFT/LoRA 微调 -> Agentic-RL | 面大模型应用/微调岗位时，用来补齐 Attention、KV Cache、LoRA 这些底层原理。 |
| 7 | ⭐⭐⭐⭐☆ | [NirDiamant/RAG_Techniques](https://github.com/NirDiamant/RAG_Techniques) | `11_rag_techniques` | 42+ 可运行 RAG 进阶技巧（语义切块、HyDE、混合检索、Rerank、GraphRAG、评估） | 企业落地最缺的不是调个 API，而是解决「RAG 搜不准、幻觉多」；学透它能拉开面试和接单报价差距。 |
| 8 | ⭐⭐⭐⭐☆ | [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners) | `06_mcp_beginners` | 微软官方 MCP（Model Context Protocol）入门，含 Python Server/Client 实战 | Cursor、Claude、各类 Agent 生态现在重度依赖 MCP；学会自写 MCP Server，接企业自动化/AI 提效单很有用。 |
| 9 | ⭐⭐⭐⭐☆ | [wesm/pydata-book](https://github.com/wesm/pydata-book) | `02_pydata_book` | Pandas 作者亲著《利用 Python 进行数据分析》第 3 版官方 Notebook | 数据分析与大数据处理基石：吃透 NumPy 向量化、Pandas 清洗/分组聚合/时间序列，后续转 Spark/Polars 或 AI 数据预处理更轻松。 |
| 10 | ⭐⭐⭐⭐ | [datawhalechina/llm-universe](https://github.com/datawhalechina/llm-universe) | `03_llm_universe` | 面向小白的大模型 API + 个人知识库 RAG + Streamlit 快速部署 | 门槛最低的 AI 应用入门实战，不要求高深数学，几天就能做出第一个可演示的 AI 知识库副业 Demo。 |
| 11 | ⭐⭐⭐⭐ | [jackfrued/Python-100-Days](https://github.com/jackfrued/python-100-days) | `01_python_100_days` | 中文最经典「从新手到数据库/Web/数据分析/机器学习」100 天路线 | 非常适合把现在 `00_basic/chapter05` 到函数、面向对象、MySQL、Pandas、后端工程的断层完整补齐。 |
| 12 | ⭐⭐⭐☆ | [TheAlgorithms/Python](https://github.com/TheAlgorithms/Python) | 暂不生成（参考） | 覆盖排序、图论、加密、机器学习的纯 Python 算法百科 | 查某类算法原理实现时极好用，但题库过庞大且缺少面试/业务讲解，只建议当字典翻阅，不要从头硬啃。 |
| 13 | ⭐⭐⭐ | [Asabeneh/30-Days-Of-Python](https://github.com/Asabeneh/30-Days-Of-Python) | 暂不生成（参考） | 英文 30 天步进式教程（基础语法 -> 异常/正则 -> Pandas -> Web/API） | 内容连贯、能顺便练英文技术阅读，但偏早期，中文资料生态不如国内项目友好。 |
| 14 | ⭐⭐⭐ | [trekhleb/learn-python](https://github.com/trekhleb/learn-python) | 暂不生成（参考） | Python 语法备忘录与带 `assert` 的单元测试卡片 | 适合当速查手册和巩固 `assert` 测试习惯，但偏向语法碎片，做不到完整项目闭环。 |

## 二、阶段路线（学习顺序）

下面假设每天能投入约 1.5 ~ 2 小时，周期仅供参考，卡住就多留几天，不要硬赶。每个阶段都有「做什么」和「验收标准」，达标再进入下一阶段。

| 阶段 | 建议周期 | 目录 | 做什么 | 验收标准 |
| --- | --- | --- | --- | --- |
| 1. 语法与算法起步 | 第 1 ~ 2 周 | `00_leetcode` | 补完 `00_basic/chapter06+`：列表、字典、集合、函数、类、异常、文件读写。同步刷 `00_warmup_basics` ~ `02_two_pointers`，每天 1 ~ 2 题，敲一遍并跑通 `assert` | 不看答案写出「两数之和」「移动零」；能说清 `list` 与 `tuple`、`dict` 与 `set` 的区别 |
| 2. 工程与数据底座 | 第 3 ~ 6 周 | `01_python_100_days`、`02_pydata_book` | Python-100-Days 只学 Day21 ~ 45（文件/JSON/数据库），pydata-book 学第 2 ~ 11 章。算法继续推到 `03_sliding_window` ~ `07_binary_tree` | 用 Pandas 完成一份真实 CSV 的清洗、分组聚合和图表；能写出带异常处理的文件读写脚本 |
| 3. LLM 应用与 RAG | 第 7 ~ 10 周 | `03_llm_universe`、`04_all_in_rag` | 先 `03_llm_universe` 跑通第一个知识库助手，再用 `04_all_in_rag` 补数据切分、向量库、混合检索和评测。算法推到 `08_backtracking` ~ `11_heap_and_trie` | 做出一个能回答自己文档的 RAG Demo，并能用评测集说明「准不准」 |
| 4. Agent 与 MCP | 第 11 ~ 16 周 | `05_hello_agents`、`06_mcp_beginners`、`07_genai_agents` | 主线学 `05_hello_agents`，配合 `06_mcp_beginners` 自写一个 MCP Server，再从 `07_genai_agents` 挑 3 ~ 5 个案例改造。算法完成 `12_graph` ~ `14_hard_capstones` | 手写一个 ReAct Agent；一个能被 Cursor 调用的 MCP Server |
| 5. 全栈交付与作品集 | 第 5 ~ 6 个月 | `08_ai_fullstack_fastapi` | 学登录、数据库、Docker、测试。把阶段 3、4 的成果包装成可部署的产品 | 至少 2 个可在线演示的项目（RAG 知识库全栈产品 + 多工具 Agent 自动化），README 写清架构与部署 |
| 6. 深挖与长期 | 第 6 个月起 | `09_happy_llm`、`10_llms_from_scratch`、`11_rag_techniques` | 想懂原理就学 `09_happy_llm`、`10_llms_from_scratch`；想做检索效果就学 `11_rag_techniques`；`TheAlgorithms/Python` 只当字典查 | 能讲清 Attention、KV Cache、LoRA；能用实验数据说明某个 RAG 优化带来的提升 |

投递与接单建议：阶段 4 结束后即可开始投简历、接小型外包。阶段 5 的作品集是长沙本地岗位、远程岗位和自由职业都通用的凭证。

## 三、挑中一行后，如何生成学习目录

仓库已配置了生成器：规则 [.cursor/rules/kpy-learning-standards.mdc](.cursor/rules/kpy-learning-standards.mdc) 自动生效，技能 [.cursor/skills/py-study-generator/SKILL.md](.cursor/skills/py-study-generator/SKILL.md) 在你提到 `py-study-generator` 时启用。

### 1. 对 AI 说一句话（任选一种）

最简版，直接写目录名：

```text
按 py-study-generator 规范初始化 02_pydata_book
```

指定范围，避免一次生成太多：

```text
按 py-study-generator 规范初始化 04_all_in_rag，只做第 1 ~ 2 章（解锁 RAG、数据准备）
```

一次挑多个，会按编号顺序逐个建好并分别验证：

```text
按 py-study-generator 规范初始化 03_llm_universe 和 05_hello_agents 的前 3 章
```

后续继续补充：

```text
用 py-study-generator 给 05_hello_agents 补第 4 章
```

### 2. 它会生成什么

- `NN_xxx/README.md`：原仓库链接、学习目标、环境与依赖、章节到本地文件的映射、进度清单。
- `NN_xxx/00_章节名/`：子目录从 `00_` 开始递增，再往下是 `00_`、`01_`... 编号的 `.py` 学习脚本。
- 每个脚本都含：顶部 Docstring（主题、难度、前置语法、在大数据/数据分析/RAG/Agent/全栈中的用途）、中文逐行注释、新手直观版与进阶版、`run_tests()` 断言和 `bootstrap()` 入口。
- 命名遵守防重名规则：不会出现 `math.py`、`json.py` 这类与标准库同名的文件。

### 3. 生成后怎么验证和学习

```bash
# 验证某个学习目录下全部脚本（导入并跑 run_tests），可一次传多个目录
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 02_pydata_book

# 单文件运行（PyCharm 里点绿色运行按钮也可以）
.venv/bin/python 02_pydata_book/00_xxx/00_xxx.py
```

学习循环：先读脚本顶部 Docstring，再自己动手改参数和输入，看 `assert` 是否仍通过，最后合上脚本自己重写一遍。

### 4. 注意事项

- **依赖**：需要第三方库的仓库（Pandas、LangChain、FastAPI、PyTorch 等），先在 `.venv` 里安装，并告诉 AI 要用哪个版本。
- **API Key**：涉及大模型的脚本，Key 一律从环境变量读取，不写进代码。`run_tests()` 必须用本地模拟数据离线通过，这样验证脚本不依赖网络和账号。
- **版权与许可**：原仓库的许可不同。例如 `NirDiamant/RAG_Techniques` 使用自定义的非商业许可，商用前要先读它的 `LICENSE`。生成的学习脚本是用自己的话重写并标注来源，不是整段拷贝；准备拿去做外包或商用的内容，建议只参考思路、自己重新实现。
- **规模控制**：Notebook 很多的仓库（如 `RAG_Techniques`、`GenAI_Agents`）建议按章节或按案例分批生成，每批 3 ~ 5 个，边生成边学。
