"""验证指定学习目录下所有 Python 脚本是否可导入并顺利通过 run_tests() 或 main 执行。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def verify_directory(target_dir: Path) -> int:
    if not target_dir.exists():
        print(f'目录不存在: {target_dir}')
        return 1

    py_files = sorted(
        path
        for path in target_dir.rglob('*.py')
        if '__pycache__' not in path.parts and path.name != '__init__.py'
    )
    if not py_files:
        print(f'未在 {target_dir} 下找到可验证的 .py 文件')
        return 1

    passed = 0
    failed: list[tuple[Path, str]] = []

    for index, file_path in enumerate(py_files):
        module_name = f'_study_verify_{index}'
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise RuntimeError('无法加载模块 spec')
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            if hasattr(module, 'run_tests'):
                module.run_tests()
            elif hasattr(module, 'bootstrap'):
                module.bootstrap()
            passed += 1
        except Exception as exc:  # noqa: BLE001
            failed.append((file_path, f'{type(exc).__name__}: {exc}'))
        finally:
            sys.modules.pop(module_name, None)

    print(f'\n验证汇总: 共 {len(py_files)} 个脚本，通过 {passed} 个，失败 {len(failed)} 个。')
    for file_path, reason in failed:
        print(f'  ❌ {file_path}: {reason}')

    return 0 if not failed else 1


if __name__ == '__main__':
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('00_leetcode')
    raise SystemExit(verify_directory(target))
