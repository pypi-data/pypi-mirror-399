# CLAUDE.md

This file provides guidance to Claude Code when working with the Nexus CLI.

## What is Nexus?

Nexus is a **knowledge workflow CLI** for academic researchers. It provides data and operations - Claude provides the thinking.

**Key Principle**: Nexus does NOT do AI. It provides structured access to:
- Zotero library (2,728 papers)
- PDFs (~1,800 files)
- Obsidian vault (knowledge notes)
- Teaching materials
- Manuscripts

## Repository Structure

```
nexus-cli/
├── nexus/                    # Python package
│   ├── cli.py               # Main CLI (Typer)
│   ├── research/            # 🔬 Zotero, PDFs, literature
│   ├── teaching/            # 📚 Courses, materials
│   ├── writing/             # ✍️ Manuscripts, LaTeX
│   ├── knowledge/           # 🧠 Vault, search
│   ├── integrations/        # 🔌 aiterm, R, Git
│   └── utils/               # Config, output
│       └── config.py        # Configuration management
│
├── plugin/                   # Claude Code plugin
│   ├── skills/              # Domain skills
│   └── commands/            # Slash commands
│
├── config/                   # Default configs
├── tests/                    # pytest tests
├── docs/                     # MkDocs documentation
├── pyproject.toml           # Project metadata
└── README.md
```

## CLI Architecture

The CLI uses **Typer** with nested subcommands:

```bash
nexus                        # Main app
├── research                 # 🔬 Research domain
│   ├── zotero              # Zotero operations
│   │   ├── search          # Search papers
│   │   └── cite            # Generate citations
│   ├── pdf                 # PDF operations
│   │   ├── extract         # Extract text
│   │   └── search          # Search PDFs
│   └── lit                 # Literature ops
├── teach                    # 📚 Teaching domain
│   ├── course              # Course management
│   └── material            # Materials search
├── write                    # ✍️ Writing domain
│   ├── manuscript          # Manuscript tracking
│   ├── bib                 # Bibliography
│   └── latex               # LaTeX helpers
├── knowledge                # 🧠 Knowledge domain
│   ├── vault               # Obsidian operations
│   └── search              # Unified search
├── integrate                # 🔌 Integrations
├── doctor                   # Health check
└── config                   # Configuration
```

## Development Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run nexus --help
uv run nexus doctor

# Run tests
uv run pytest

# Type check
uv run mypy nexus/

# Lint
uv run ruff check nexus/
```

## Configuration

Configuration is stored at `~/.config/nexus/config.yaml`:

```yaml
zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

vault:
  path: ~/Obsidian/Nexus
  templates: ~/Obsidian/Nexus/_SYSTEM/templates

pdf:
  directories:
    - ~/Documents/Research/PDFs
    - ~/Documents/Teaching/PDFs
```

## Adding New Commands

1. **Find the domain** in `nexus/cli.py`
2. **Add a subcommand** using the `@<domain>_app.command()` decorator
3. **Use Typer Annotations** for arguments and options
4. **Output with Rich** for beautiful formatting

Example:
```python
@research_app.command()
def new_command(
    query: Annotated[str, typer.Argument(help="The query")],
    limit: Annotated[int, typer.Option("--limit", "-n")] = 10,
) -> None:
    """Description of the command."""
    console.print(f"Running with query: {query}")
```

## Adding Domain Logic

1. Create a module in the domain folder (e.g., `nexus/research/zotero.py`)
2. Create a class or functions for the operations
3. Import and use in `cli.py`

Example:
```python
# nexus/research/zotero.py
class ZoteroClient:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def search(self, query: str) -> List[dict]:
        # Implementation
        ...

# nexus/cli.py
from nexus.research.zotero import ZoteroClient

@zotero_app.command("search")
def zotero_search(query: str) -> None:
    client = ZoteroClient(config.zotero.database)
    results = client.search(query)
    # Display results
```

## Claude Integration Patterns

### Pattern 1: Claude Calls Nexus (Primary)
```bash
# In Claude Code, Claude runs:
nexus research zotero search "mediation" --json
```

### Pattern 2: Pipe to Claude
```bash
nexus knowledge search "topic" --json | claude -p "Summarize"
```

### Pattern 3: Plugin Skills
Skills in `plugin/skills/` teach Claude how to use nexus effectively.

## Testing

```bash
# Run all tests
uv run pytest

# Run specific domain
uv run pytest tests/research/

# With coverage
uv run pytest --cov=nexus
```

## Code Style

- **Line length**: 100 characters
- **Formatting**: Ruff
- **Type hints**: Required (mypy strict)
- **Docstrings**: Google style

## Implementation Phases

| Phase | Focus | Hours | Status |
|-------|-------|-------|--------|
| 1 | Core Infrastructure | 4h | ✅ Done |
| 2 | Knowledge Domain | 3h | Next |
| 3 | Research Domain | 4h | Pending |
| 4 | Teaching & Writing | 3h | Pending |
| 5 | Claude Plugin | 3h | Pending |
| 6 | Testing & Docs | 3h | Pending |
