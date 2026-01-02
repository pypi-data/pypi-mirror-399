# Plan for Building MCP Server - agent-coding-standards-mcp

## 🎯 Project Overview

**Repository Name:** `agent-coding-standards-mcp`

**Description:** MCP Server for managing AI coding agent guidelines, workflows, and rules

**Tech Stack:**
- **Package Manager:** `uv` (fast Python package installer)
- **Language:** Python 3.13.3
- **MCP:** Python SDK for stdio server
- **Code Quality:**
  - `ruff` - linting & formatting
  - `mypy` - static type checking
- **Source:** GitLab (company private repo)
- **Optional:** FastAPI for web interface

---

## 📋 Phase 1: Project Setup & Tooling

### 1.1 Initialize Project with UV

**Project Structure:**
```
agent-coding-standards-mcp/
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── .python-version
│
├── guidelines/
│   ├── cline/
│   │   ├── config/
│   │   ├── workflows/
│   │   └── rules/
│   │
│   ├── claude/
│   │   ├── config/
│   │   ├── workflows/
│   │   └── rules/
│   │
│   └── copilot/
│       ├── config/
│       ├── workflows/
│       └── rules/
│
├── src/
│   └── agent_coding_standards_mcp/
│       ├── tools/
│       ├── services/
│       ├── models/
│       └── utils/
│
└── tests/
```

### 1.2 pyproject.toml Configuration

**pyproject.toml:**
```toml
[project]
name = "agent-coding-standards-mcp"
version = "0.1.0"
description = "MCP Server for AI coding agent standards"
authors = [{name = "Teqnological", email = "dev@teqnological.asia"}]
readme = "README.md"
requires-python = ">=3.13"

dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0",
    "aiohttp>=3.9",
    "aiofiles>=23.0",
    "python-frontmatter>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=6.0",
    "mypy>=1.13",
    "ruff>=0.8",
    "pre-commit>=3.7",
]

[project.scripts]
agent-mcp-server = "agent_coding_standards_mcp.server:main"

[tool.mypy]
python_version = "3.13"
explicit_package_bases = true
namespace_packages = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_optional = true
exclude = [
    "tests/",
]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--cov=src/agent_coding_standards_mcp",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=80",
]
testpaths = ["tests"]
pythonpath = ["."]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/.venv/*",
    "*/__init__.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod",
]
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**.ruff.toml:**
```toml
exclude = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pyenv",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    ".vscode",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
]

line-length = 88
indent-width = 4
target-version = "py313"

[lint]
select = [
    "E4", "E7", "E9", "F",
    "W",
    "C901",
    "I",
    "N",
    "UP",
    "B",
    "C4",
]
ignore = [
    "E501",
]

fixable = ["ALL"]
unfixable = []

dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
docstring-code-format = false
docstring-code-line-length = "dynamic"
```

**.mise.toml:**
```toml
[tools]
python = "3.13.3"
uv = "0.7.18"

[tasks.setup]
run = """
mise install
uv sync
uv run pre-commit install
"""

[tasks.format]
run = "uv run ruff format ."

[tasks.lint]
run = "uv run ruff check . --fix"

[tasks.typecheck]
run = "uv run mypy src/"

[tasks.test]
run = "uv run pytest"

[tasks.test-unit]
run = "uv run pytest -m unit"

[tasks.test-integration]
run = "uv run pytest -m integration"

[tasks.test-cov]
run = "uv run pytest --cov --cov-report=html"

[tasks.check]
run = """
mise format
mise lint
mise typecheck
mise test
"""

[tasks.pre-commit]
run = "uv run pre-commit run --all-files"
```

**.pre-commit-config.yaml:**
```yaml
repos:
  - repo: local
    hooks:
      - id: format
        name: format
        entry: bash -c 'mise format'
        language: system
        files: \.py$
        pass_filenames: false
        
      - id: lint
        name: lint
        entry: bash -c 'mise lint'
        language: system
        files: \.py$
        pass_filenames: false
        
      - id: typecheck
        name: typecheck
        entry: bash -c 'mise typecheck'
        language: system
        files: \.py$
        pass_filenames: false
        
      - id: test
        name: test
        entry: bash -c 'mise test'
        language: system
        files: \.py$
        pass_filenames: false
```