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

**Current Version**: 0.5.0

## Quick Start for Claude

```bash
# Check installation
nexus --version              # Should show 0.5.0
nexus doctor                 # Health check

# Interactive learning system
nexus learn                  # List all tutorials
nexus learn getting-started  # Start beginner tutorial
nexus learn medium          # Domain workflows
nexus learn advanced        # Power user techniques

# Common operations
nexus research zotero search "query" --json
nexus knowledge vault search "query" --json
nexus write manuscript list --json
```

## Repository Structure

```
nexus-cli/
├── nexus/                    # Python package
│   ├── cli.py               # Main CLI (Typer) - Entry point
│   ├── research/            # 🔬 Zotero, PDFs, literature
│   ├── teaching/            # 📚 Courses, Quarto materials
│   ├── writing/             # ✍️ Manuscripts, LaTeX, bibliography
│   ├── knowledge/           # 🧠 Vault, search, graph
│   ├── integrations/        # 🔌 aiterm, R, Git
│   └── utils/               # Config, tutorial, output
│       ├── config.py        # Configuration management
│       └── tutorial.py      # Interactive tutorial system (NEW v0.5.0)
│
├── plugin/                   # Claude Code plugin
│   ├── skills/              # Domain skills
│   └── commands/            # Slash commands
│
├── docs/                     # MkDocs documentation
│   ├── getting-started/     # Installation, quickstart
│   ├── tutorials/           # Interactive tutorial docs (NEW)
│   ├── guide/               # User guides by domain
│   ├── reference/           # CLI, API, MCP reference
│   └── development/         # Contributing, testing
│
├── tests/                    # pytest tests (422 tests, 75% coverage)
├── config/                   # Default configs
├── pyproject.toml           # Project metadata
└── README.md
```

## CLI Architecture

The CLI uses **Typer** with nested subcommands organized by domain:

```bash
nexus                        # Main app
├── doctor                   # Health check (verify installation)
├── config                   # View/edit configuration
├── learn                    # 🎓 Interactive tutorials (NEW v0.5.0)
│   ├── (no args)           # List all tutorials
│   ├── getting-started     # Beginner (7 steps, ~10 min)
│   ├── medium              # Intermediate (11 steps, ~20 min)
│   └── advanced            # Expert (12 steps, ~30 min)
│
├── research                 # 🔬 Research domain
│   ├── zotero              # Zotero operations
│   │   ├── search          # Search papers
│   │   ├── get             # Get paper details
│   │   ├── cite            # Generate citations
│   │   ├── recent          # Recent additions
│   │   ├── tags            # List tags
│   │   └── by-tag          # Filter by tag
│   └── pdf                 # PDF operations
│       ├── extract         # Extract text
│       └── search          # Search PDFs
│
├── teach                    # 📚 Teaching domain
│   ├── course              # Course management
│   │   ├── list            # List courses
│   │   └── show            # Show course details
│   └── quarto              # Quarto operations
│       ├── build           # Build project
│       ├── preview         # Preview locally
│       └── info            # Show project info
│
├── write                    # ✍️ Writing domain
│   ├── manuscript          # Manuscript tracking
│   │   ├── list            # List manuscripts
│   │   ├── show            # Show details
│   │   ├── stats           # Show statistics
│   │   ├── batch-status    # Batch update status (v0.5.0)
│   │   ├── batch-progress  # Batch update progress (v0.5.0)
│   │   └── export          # Export metadata (v0.5.0)
│   └── bib                 # Bibliography
│       └── check           # Check citations
│
├── knowledge                # 🧠 Knowledge domain
│   ├── vault               # Obsidian operations
│   │   ├── search          # Search notes
│   │   ├── read            # Read note
│   │   ├── recent          # Recent notes
│   │   ├── graph           # Generate graph
│   │   ├── export          # Export graph (v0.5.0)
│   │   │   ├── graphml     # For Gephi/Cytoscape
│   │   │   ├── d3          # For D3.js visualizations
│   │   │   └── json        # JSON format
│   │   └── orphans         # Find orphaned notes
│   └── search              # Unified search (all sources)
│
└── integrate                # 🔌 Integrations
    └── (various integration commands)
```

## Key Features (v0.5.0)

### 🎓 Interactive Tutorial System (NEW)
- **3 progressive levels**: getting-started, medium, advanced
- **30 total steps** with hands-on exercises
- **Self-paced**: pause and resume with `--step N`
- **Real commands**: practice with actual data
- **Contextual hints**: guidance at each step

```bash
nexus learn                  # Show all tutorials
nexus learn getting-started  # Start beginner
nexus learn medium --step 5  # Resume from step 5
```

### 📊 Graph Export (v0.5.0)
- Export vault knowledge graphs to multiple formats
- GraphML for Gephi, Cytoscape, yEd
- D3.js format for web visualizations
- JSON with tag support

```bash
nexus knowledge vault export graphml graph.graphml
nexus knowledge vault export d3 graph.json --limit 100
```

### 📝 Batch Manuscript Operations (v0.5.0)
- Update status for multiple manuscripts
- Batch progress tracking
- Export metadata to JSON/CSV

```bash
nexus write manuscript batch-status paper1 paper2 --status under_review
nexus write manuscript batch-progress paper1:75 paper2:90
nexus write manuscript export manuscripts.json
```

### 🔍 Unified Search
- Search across Zotero, vault, and PDFs simultaneously
- Filter by source
- JSON output for Claude integration

```bash
nexus knowledge search "propensity score" --json
nexus knowledge search "mediation" --source zotero,vault
```

## Development Commands

```bash
# Install dependencies
uv sync

# Run CLI locally
uv run nexus --help
uv run nexus doctor
uv run nexus learn

# Install as tool (recommended)
uv tool install .
uv tool install --reinstall .  # For updates

# Run tests
uv run pytest                  # All tests (422 tests)
uv run pytest --cov=nexus     # With coverage (75%)
uv run pytest tests/research/ # Specific domain

# Type check
uv run mypy nexus/

# Lint
uv run ruff check nexus/

# Documentation
uv run mkdocs serve           # Preview docs locally
uv run mkdocs build           # Build docs
uv run mkdocs gh-deploy       # Deploy to GitHub Pages
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

teaching:
  courses_dir: ~/projects/teaching

writing:
  manuscripts_dir: ~/projects/research
```

**Environment Override**: Set `NEXUS_CONFIG=/path/to/config.yaml` to use alternate config.

## Adding New Commands

### 1. Find the Domain
Identify which domain app in `nexus/cli.py`:
- `research_app` - Research operations
- `teach_app` - Teaching operations
- `write_app` - Writing operations
- `knowledge_app` - Knowledge operations
- `integrate_app` - Integrations
- `app` - Top-level commands

### 2. Add Subcommand

```python
@research_app.command()
def new_command(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n")] = 10,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    """Description of what this command does."""
    import json
    
    # Your logic here
    results = do_something(query, limit)
    
    if json_output:
        console.print(json.dumps(results, indent=2))
    else:
        # Use Rich for beautiful formatting
        from rich.table import Table
        table = Table(show_header=True)
        table.add_column("Column 1")
        table.add_column("Column 2")
        for item in results:
            table.add_row(item.field1, item.field2)
        console.print(table)
```

### 3. Use Existing Patterns
- **Arguments**: Required positional parameters
- **Options**: Optional flags with `--flag` or `-f`
- **JSON output**: Always support `--json` for Claude integration
- **Rich formatting**: Use tables, panels, syntax for terminal output
- **Error handling**: Print helpful error messages

## Adding Domain Logic

### 1. Create Module
Create a new file in the appropriate domain folder:
```
nexus/research/new_feature.py
nexus/teaching/new_feature.py
nexus/writing/new_feature.py
nexus/knowledge/new_feature.py
```

### 2. Implement Logic

```python
# nexus/research/new_feature.py
from pathlib import Path
from typing import List, Dict

class NewFeature:
    """Feature description."""
    
    def __init__(self, config_param: Path):
        self.config_param = config_param
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search implementation."""
        # Your logic here
        results = []
        return results
```

### 3. Import and Use in CLI

```python
# In nexus/cli.py
from nexus.research.new_feature import NewFeature

@research_app.command("new-feature")
def new_feature_command(query: str) -> None:
    """Use the new feature."""
    config = get_config()
    feature = NewFeature(config.some_param)
    results = feature.search(query)
    # Display results
```

## Claude Integration Patterns

### Pattern 1: Direct Execution (Primary)
Claude runs nexus commands directly:

```bash
# In Claude Code, Claude executes:
nexus research zotero search "mediation analysis" --json
nexus knowledge vault search "causal inference" --json
nexus write manuscript list --json
```

### Pattern 2: JSON Pipelines
Pipe nexus output to Claude for analysis:

```bash
nexus knowledge search "methods" --json | claude -p "Summarize these results"
nexus research zotero recent --limit 20 --json > papers.json
```

### Pattern 3: Plugin Skills
Skills in `plugin/skills/` teach Claude domain-specific workflows:
- `knowledge/vault-operations/` - Vault search and management
- `research/zotero-integration/` - Literature management
- `writing/manuscript-management/` - Manuscript tracking
- `teaching/course-management/` - Course operations

### Pattern 4: Interactive Tutorials
Claude can guide users through learning:

```bash
# Claude recommends:
nexus learn                  # Browse tutorials
nexus learn getting-started  # Start learning
```

## Testing

```bash
# Run all tests (422 tests)
uv run pytest

# Run with coverage (current: 75%)
uv run pytest --cov=nexus

# Run specific test file
uv run pytest tests/test_zotero.py

# Run specific domain
uv run pytest tests/research/
uv run pytest tests/knowledge/

# Run with verbose output
uv run pytest -v

# Run failed tests only
uv run pytest --lf

# Run in parallel (faster)
uv run pytest -n auto
```

## Code Style

- **Line length**: 100 characters
- **Formatting**: Ruff (`uv run ruff format nexus/`)
- **Linting**: Ruff (`uv run ruff check nexus/`)
- **Type hints**: Required (mypy strict)
- **Docstrings**: Google style
- **Import order**: isort-compatible (enforced by ruff)

## Installation Methods

### For Development (You)
```bash
cd /Users/dt/projects/dev-tools/nexus-cli
uv tool install --reinstall .
```

### For Users (After PyPI Publication)
```bash
# Recommended
uv tool install nexus-cli

# Alternative methods
pip install nexus-cli
pipx install nexus-cli

# From GitHub
uv tool install git+https://github.com/Data-Wise/nexus-cli

# Homebrew (after PyPI publication)
brew tap data-wise/tap
brew install nexus-cli
```

### Troubleshooting Installation

**Name collision**: Don't use `uv tool install nexus` (different package on PyPI)
**Always use**: `uv tool install nexus-cli`

**Shell alias conflict**: Check for conflicting aliases:
```bash
type nexus  # Should show: nexus is /Users/dt/.local/bin/nexus
grep "alias nexus" ~/.zshrc ~/.config/zsh/.zshrc
```

**PATH issues**: Ensure `~/.local/bin` is in PATH:
```bash
echo $PATH | grep ".local/bin"
```

## Project Status

### Completed Features (v0.5.0)
✅ Core CLI infrastructure (Typer, Rich)
✅ Research domain (Zotero, PDFs)
✅ Knowledge domain (Vault, search, graph)
✅ Teaching domain (Courses, Quarto)
✅ Writing domain (Manuscripts, bibliography)
✅ Interactive tutorial system (3 levels, 30 steps)
✅ Graph export (GraphML, D3.js, JSON)
✅ Batch manuscript operations
✅ MCP server integration (17 tools)
✅ Comprehensive documentation (MkDocs)
✅ Testing infrastructure (422 tests, 75% coverage)
✅ CI/CD (GitHub Actions, multi-platform)

### Key Metrics
- **Version**: 0.5.0
- **Tests**: 422 passing (75% coverage)
- **Commands**: 50+ across 4 domains
- **Documentation**: 9,500+ lines (MkDocs)
- **Tutorial Steps**: 30 (interactive learning)
- **Python**: 3.11+ required

### File Locations to Know
- **Main CLI**: `nexus/cli.py` (1,900+ lines)
- **Tutorial System**: `nexus/utils/tutorial.py` (500+ lines)
- **Config Management**: `nexus/utils/config.py`
- **Tests**: `tests/` (422 tests)
- **Docs**: `docs/` (MkDocs site)
- **Tutorial Docs**: 
  - `TUTORIAL_GUIDE.md` (2,000 lines)
  - `TUTORIAL_QUICK_REF.md` (300 lines)
  - `docs/tutorials/tutorial-system.md` (10,000 lines)

## Quick Reference for Common Tasks

### Search Operations
```bash
# Search Zotero
nexus research zotero search "query" --json

# Search vault
nexus knowledge vault search "query" --json

# Unified search
nexus knowledge search "query" --source all --json
```

### Data Export
```bash
# Export graph
nexus knowledge vault export graphml graph.graphml
nexus knowledge vault export d3 graph.json

# Export manuscripts
nexus write manuscript export data.json --format json
nexus write manuscript export data.csv --format csv
```

### Learning & Help
```bash
# Interactive tutorials
nexus learn
nexus learn getting-started

# Command help
nexus --help
nexus research zotero --help
nexus learn --help

# Health check
nexus doctor
```

## Notes for Claude

1. **Always use --json** when piping output to analysis
2. **Check nexus doctor** if commands fail
3. **Use tutorials** to learn workflows: `nexus learn`
4. **Version-specific features**: Check version with `nexus --version`
5. **Configuration required**: Many features need `~/.config/nexus/config.yaml`
6. **Package name**: Install as `nexus-cli`, not `nexus` (name collision)

## Recent Changes (v0.5.0)

- ✅ Renamed `tutorial` command to `learn` (simpler)
- ✅ Removed "run" action (direct execution)
- ✅ Added interactive tutorial system (3 levels)
- ✅ Added graph export formats
- ✅ Added batch manuscript operations
- ✅ Updated all documentation
- ✅ MkDocs integration for tutorials
- ✅ 422 tests passing (75% coverage)
