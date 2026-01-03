# Contributing to Nexus CLI

Thank you for your interest in contributing to Nexus CLI!

## Development Setup

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Clone and Install

```bash
git clone https://github.com/Data-Wise/nexus-cli.git
cd nexus-cli

# Install with dev dependencies
uv sync

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=nexus

# Run specific test file
uv run pytest tests/test_vault.py

# Run tests matching a pattern
uv run pytest -k "search"
```

### Code Quality

```bash
# Lint with ruff
uv run ruff check nexus/

# Format code
uv run ruff format nexus/

# Type check with mypy
uv run mypy nexus/
```

## Project Structure

```
nexus-cli/
├── nexus/                    # Main package
│   ├── cli.py               # CLI entry point (Typer)
│   ├── knowledge/           # Knowledge domain
│   ├── research/            # Research domain
│   ├── teaching/            # Teaching domain
│   ├── writing/             # Writing domain
│   └── utils/               # Shared utilities
├── tests/                    # pytest tests
├── docs/                     # Documentation
└── plugin/                   # Claude Code plugin
```

## Adding a New Command

1. **Find the domain** - Commands are organized by domain in `cli.py`
2. **Add the command** - Use `@<domain>_app.command()` decorator
3. **Add tests** - Add tests in `tests/test_cli.py`
4. **Update docs** - Update `docs/reference/cli.md`

Example:

```python
@research_app.command("new-cmd")
def new_command(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n")] = 10,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Description of the command."""
    # Implementation
    if json_output:
        console.print_json(data=results)
    else:
        # Rich table output
        ...
```

## Pull Request Guidelines

1. **Create a branch** - `git checkout -b feature/my-feature`
2. **Make changes** - Keep commits focused
3. **Add tests** - All new features need tests
4. **Run checks** - `pytest && ruff check && mypy`
5. **Submit PR** - Reference any related issues

## Commit Messages

Follow conventional commits:

```
feat: add new command for X
fix: handle edge case in Y
docs: update CLI reference
test: add tests for Z
refactor: simplify config loading
```

## Code Style

- **Line length**: 100 characters
- **Formatting**: ruff format
- **Type hints**: Required
- **Docstrings**: Google style

## Questions?

Open an issue on GitHub or check existing issues for similar questions.
