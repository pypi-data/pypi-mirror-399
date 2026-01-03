---
description: Bump version and publish to PyPI
---

1. Run tests to ensure stability and version sync
// turbo
```bash
uv run pytest
```

2. Update `version` in `pyproject.toml`
3. Update `__version__` in `py_invoices/__init__.py`

4. Verify strict version match
// turbo
```bash
uv run pytest tests/unit/test_version.py
```

5. Build the package
// turbo
```bash
rm -rf dist && uv build
```

6. Publish to PyPI (requires manual credential entry)
```bash
uv publish
```
