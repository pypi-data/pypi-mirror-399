# Nexus CLI

**Knowledge workflow CLI for research, teaching, and writing**

[![CI](https://github.com/Data-Wise/nexus-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/Data-Wise/nexus-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/Data-Wise/nexus-cli)

---

## Philosophy

**Nexus does NOT do AI. It provides data and operations. Claude does the thinking.**

Nexus is Claude's **body** for academic work—providing structured access to your knowledge base without doing any AI processing itself.

## Quick Example

```bash
# Search your entire knowledge system
nexus knowledge search "mediation analysis"

# Find papers in Zotero
nexus research zotero search "causal inference" --limit 5

# Check manuscript citations
nexus write bib check my-paper

# Generate vault graph visualization
nexus knowledge vault graph --json > graph.json
```

## Features

- **🧠 Knowledge Management**: Obsidian vault operations with graph visualization
- **🔬 Research Tools**: Zotero library search and PDF extraction
- **📚 Teaching Support**: Course management and Quarto integration
- **✍️ Writing Assistance**: Manuscript tracking and bibliography checking
- **🔌 Claude Integration**: MCP server with 17 tools for Claude Desktop/Code
- **📊 Unified Search**: Query across vault, Zotero, and PDFs simultaneously

## Architecture

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

## Getting Started

Ready to set up Nexus? Follow our [Installation Guide](getting-started/installation.md) to get started in minutes.

## Use Cases

### For Researchers
- Quickly search your entire Zotero library from the command line
- Extract and search PDF content across thousands of papers
- Track manuscript progress and check bibliography completeness
- Generate citation keys and formatted references

### For Teachers
- Manage course materials and syllabi
- Track lecture slides and assignments
- Build and preview Quarto course websites
- Organize teaching resources

### For Knowledge Workers
- Search your Obsidian vault with powerful queries
- Visualize note connections with graph data
- Find orphaned notes and broken links
- Unified search across all your knowledge sources

## Next Steps

- **New to Nexus?** Start with the [Quick Start Guide](getting-started/quickstart.md)
- **Want to configure?** See the [Configuration Guide](getting-started/configuration.md)
- **Looking for examples?** Check out the [Tutorials](tutorials/first-steps.md)
- **Need the API reference?** Visit the [Command Reference](reference/cli.md)

## License

MIT License - see [LICENSE](https://github.com/Data-Wise/nexus-cli/blob/main/LICENSE) for details.
