---
name: py-study-generator
description: >-
  Generate structured Python 3.12 learning modules for kpy_project, including
  00_leetcode algorithm lessons and sibling 00_xxx GitHub study modules from
  beginner to mastery. Produces 00_xx numbered directories and files, multiple
  annotated solutions, complexity comparisons, real-world AI/data engineering
  connections, and runnable assert tests. Use when adding LeetCode problems,
  expanding a 00_leetcode topic, creating a new 00_xxx learning repository
  module, or auditing study scripts.
---

# Python Study Generator (`kpy_project`)

Generate beginner-friendly yet production-grade Python 3.12 learning files aligned with `kpy_project` conventions (`bootstrap()`, Chinese line-by-line explanations, multi-approach progression, and zero standard-library shadowing).

## Workflow

1. **Determine the target track**:
   - **Adding to `00_leetcode/`** -> Read [leetcode-roadmap.md](references/leetcode-roadmap.md) to pick the right `00_xx` topic folder and the next `00_` index (ordered Easy -> Medium -> Hard).
   - **Adding a sibling `00_xxx/` module** (e.g., `00_pydata_book`, `00_all_in_rag`, `00_hello_agents`) -> Follow the same `00_xx` chapter + `00_xx` lesson numbering inside `<repo-root>/00_<topic>/`.
2. **Read the code template**:
   - Load [templates.md](references/templates.md) before writing `.py` or `README.md` files.
3. **Author with strict safety & clarity rules**:
   - Never name a `.py` file after a stdlib/popular module (`math.py`, `json.py`, `random.py`, `string.py`, `types.py`). Prefixing with `00_`, `01_`, or `exp_` prevents import shadowing.
   - Never shadow Python builtins (`sum`, `list`, `dict`, `str`, `id`, `min`, `max`, `len`). Use `total`, `nums`, `items`, `seen`, `counts`.
   - Include at least two approaches when pedagogical value exists: an intuitive/brute-force version (annotated step by step) and an optimal/Pythonic version.
   - Explain **why** each optimization works and **where** it appears in Data Analysis, Big Data, LLM/RAG, AI Agent, or Full-Stack engineering.
   - Include `run_tests()` with edge cases (empty input, single item, duplicates, negatives, boundary limits) and call `run_tests()` inside `bootstrap()`.
4. **Update the folder `README.md`**:
   - Keep the checklist table in `00_leetcode/README.md` and the topic's `README.md` synchronized (`[x]` vs `[ ]`).
5. **Verify execution**:
   - Run the verification script against the created/updated directory before finishing:

```bash
.venv/bin/python .cursor/skills/py-study-generator/scripts/verify_modules.py 00_leetcode
```

## Additional Resources

- Problem templates & comment conventions: [templates.md](references/templates.md)
- Complete Easy-to-Hard `00_leetcode` syllabus: [leetcode-roadmap.md](references/leetcode-roadmap.md)
- Module test runner: [verify_modules.py](scripts/verify_modules.py)
