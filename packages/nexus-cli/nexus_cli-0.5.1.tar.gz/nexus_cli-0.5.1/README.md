# Nexus CLI

[![CI](https://github.com/Data-Wise/nexus-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/ci.yml)
[![Documentation](https://github.com/Data-Wise/nexus-cli/actions/workflows/docs.yml/badge.svg)](https://data-wise.github.io/nexus-cli)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](https://github.com/Data-Wise/nexus-cli/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/Data-Wise/nexus-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/Data-Wise/nexus-cli)
[![Tests](https://img.shields.io/badge/tests-422%20passing-success.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-75%25-green.svg)](https://codecov.io/gh/Data-Wise/nexus-cli)
[![Code Quality](https://github.com/Data-Wise/nexus-cli/workflows/Code%20Quality/badge.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/quality.yml)

> **Knowledge workflow CLI for research, teaching, and writing.**
> Claude is the brain, Nexus is the body.

**📚 [Documentation](https://data-wise.github.io/nexus-cli)** | **🚀 [Quick Start](https://data-wise.github.io/nexus-cli/getting-started/quickstart/)** | **📖 [Changelog](https://data-wise.github.io/nexus-cli/changelog/)**

```
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗          ║
    ║     ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝          ║
    ║     ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗          ║
    ║     ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║          ║
    ║     ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║          ║
    ║     ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝          ║
    ║                                                           ║
    ║         Research • Teaching • Writing • Knowledge         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
```

## Philosophy

**Nexus does NOT do AI. It provides data and operations. Claude does the thinking.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE NEXUS ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      ┌─────────────┐                           │
│                      │   CLAUDE    │  (Brain)                  │
│                      │ • Thinking  │                           │
│                      │ • Planning  │                           │
│                      │ • Writing   │                           │
│                      └──────┬──────┘                           │
│                             │                                   │
│                             │ uses                              │
│                             ▼                                   │
│                      ┌─────────────┐                           │
│                      │   NEXUS     │  (Body)                   │
│                      │ • Searching │                           │
│                      │ • Reading   │                           │
│                      │ • Writing   │                           │
│                      │ • Organizing│                           │
│                      └──────┬──────┘                           │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              ▼              ▼              ▼                   │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│       │  ZOTERO  │   │   PDFs   │   │  VAULT   │              │
│       │  2,728   │   │  1,800   │   │ Obsidian │              │
│       │  papers  │   │  files   │   │  notes   │              │
│       └──────────┘   └──────────┘   └──────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# From source (recommended)
git clone https://github.com/Data-Wise/nexus-cli
cd nexus-cli
pip install -e .

# Or with uv
uv sync
```

## Quick Start

### New to Nexus? Start with Interactive Tutorials! 🎓

```bash
# List available tutorials
nexus learn

# Start the Getting Started tutorial (7 steps, ~10 min)
nexus learn getting-started

# Intermediate workflows (11 steps, ~20 min)
nexus learn medium

# Advanced techniques (12 steps, ~30 min)
nexus learn advanced
```

See [TUTORIAL_GUIDE.md](TUTORIAL_GUIDE.md) for detailed tutorial documentation.

### Quick Commands

```bash
# Check your setup
nexus doctor

# Configure paths
nexus config

# Search your Zotero library
nexus research zotero search "mediation analysis"

# Search your vault
nexus knowledge vault search "sensitivity"

# Unified search across everything
nexus knowledge search "propensity score"
```

## Command Reference

### Global Commands

| Command | Description |
|---------|-------------|
| `nexus doctor` | Check Nexus health and integrations |
| `nexus config` | View or edit configuration |
| `nexus learn` | Interactive learning tutorials (getting-started, medium, advanced) |
| `nexus --version` | Show version |

---

### 🧠 Knowledge Domain

Obsidian vault and unified search operations.

#### Unified Search
```bash
nexus knowledge search "query"              # Search across all sources
```

#### Vault Operations
```bash
nexus knowledge vault search "term"         # Search vault notes
nexus knowledge vault read "path/note.md"   # Read a note
nexus knowledge vault write "path" content  # Write to a note
nexus knowledge vault daily                 # Open/create daily note
nexus knowledge vault backlinks "note.md"   # Find notes linking here
nexus knowledge vault recent                # Show recently modified
nexus knowledge vault orphans               # Find unlinked notes
nexus knowledge vault template "name"       # Create from template
```

#### Graph Export ⭐ NEW in v0.5.0
```bash
# Export vault graph to multiple formats
nexus knowledge vault export graphml graph.graphml    # GraphML (Gephi, Cytoscape)
nexus knowledge vault export d3 graph.json            # D3.js visualization
nexus knowledge vault export json graph.json          # JSON format

# Include tags as nodes
nexus knowledge vault export graphml graph.graphml --tags

# Limit node count for large vaults
nexus knowledge vault export d3 graph.json --limit 100
```

---

### 🔬 Research Domain

Literature management, Zotero, and PDF operations.

#### Zotero Operations
```bash
nexus research zotero search "query"        # Search Zotero library
nexus research zotero get KEY               # Get item details
nexus research zotero cite KEY              # Generate citation
nexus research zotero recent                # Recently modified items
nexus research zotero tags                  # List all tags
nexus research zotero collections           # List all collections
nexus research zotero by-tag "tag"          # Items with specific tag
```

#### PDF Operations
```bash
nexus research pdf extract FILE             # Extract text from PDF
nexus research pdf search "query"           # Search across PDFs
nexus research pdf list                     # List all PDFs
nexus research pdf info FILE                # Show PDF information
```

---

### 📚 Teaching Domain

Course management and Quarto operations.

#### Course Management
```bash
nexus teach course list                     # List all courses
nexus teach course show NAME                # Show course details
nexus teach course lectures NAME            # List course lectures
nexus teach course materials NAME           # List all materials
nexus teach course syllabus NAME            # Show syllabus
```

#### Quarto Operations
```bash
nexus teach quarto build                    # Build Quarto project
nexus teach quarto preview                  # Start preview server
nexus teach quarto info                     # Show Quarto info
nexus teach quarto clean                    # Clean build artifacts
nexus teach quarto formats                  # List output formats
```

---

### ✍️ Writing Domain

Manuscript and bibliography management.

#### Manuscript Management
```bash
nexus write manuscript list                 # List all manuscripts
nexus write manuscript show NAME            # Show manuscript details
nexus write manuscript active               # Show active manuscripts
nexus write manuscript search "query"       # Search manuscripts
nexus write manuscript stats                # Show statistics
nexus write manuscript deadlines            # Show deadlines/targets
```

#### Batch Operations ⭐ NEW in v0.5.0
```bash
# Update status for multiple manuscripts
nexus write manuscript batch-status paper1 paper2 --status review

# Update progress for multiple manuscripts
nexus write manuscript batch-progress paper1:75 paper2:90 paper3:50

# Archive old manuscripts
nexus write manuscript batch-archive old-paper1 old-paper2

# Export metadata to JSON or CSV
nexus write manuscript export manuscripts.json
nexus write manuscript export manuscripts.csv --format csv
```

#### Bibliography Operations
```bash
nexus write bib list MANUSCRIPT             # List bibliography entries
nexus write bib search "query"              # Search bibliography
nexus write bib check MANUSCRIPT            # Check citations (missing/unused)
nexus write bib zotero "query"              # Search Zotero for entries
```

---

### 🔌 Integration Domain

External tool integrations.

```bash
nexus integrate aiterm                      # Manage aiterm integration
nexus integrate claude                      # Manage Claude plugin
```

---

## JSON Output

All commands support `--json` for machine-readable output:

```bash
nexus write manuscript stats --json | jq '.total_manuscripts'
nexus research zotero search "mediation" --json | jq '.[0].title'
```

## Claude Integration

Nexus is designed to work with Claude via:

### 1. Piping to Claude Code
```bash
nexus research zotero search "mediation" --json | \
  claude -p "Summarize these papers"
```

### 2. Claude Calls Nexus (Primary Pattern)
In Claude Code, Claude uses Bash to call nexus commands directly.

### 3. Claude Code Plugin
Install the included plugin for enhanced Claude Code integration:
```bash
ln -sf /path/to/nexus-cli/plugin ~/.claude/plugins/nexus-cli
```

## Configuration

Configuration file: `~/.config/nexus/config.yaml`

```yaml
vault:
  path: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents
  templates: ~/path/to/templates

zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

teaching:
  courses_dir: ~/projects/teaching

writing:
  manuscripts_dir: ~/projects/quarto/manuscripts
```

```bash
# View config
nexus config

# Edit config (opens in $EDITOR)
nexus config --edit
```

## What's New in v0.4.0

🎉 **Major Release** - Production-ready with enterprise-grade quality!

- **✅ 235 Tests** with 53% coverage (+10% from v0.3.0)
- **🔄 Enhanced CI/CD** with matrix testing, security scanning, and coverage enforcement
- **📚 Full Documentation** site with MkDocs + Material theme
- **🧪 Advanced Testing** for PDF, Zotero, and Quarto modules
- **🔒 Security** scanning with Bandit
- **📊 Coverage Thresholds** enforced at 40%+

See the full [Changelog](https://data-wise.github.io/nexus-cli/changelog/) for details.

## Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=nexus --cov-report=html

# Specific test file
pytest tests/test_vault.py

# Skip integration tests
pytest -m "not integration"
```

### Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/Data-Wise/nexus-cli/blob/main/CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Data-Wise/nexus-cli
cd nexus-cli

# Install with development dependencies
pip install -e ".[dev,docs]"

# Run tests
pytest

# Build documentation locally
mkdocs serve
```

## License

MIT
