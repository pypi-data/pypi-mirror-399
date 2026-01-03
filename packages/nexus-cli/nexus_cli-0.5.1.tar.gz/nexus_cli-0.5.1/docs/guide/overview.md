# User Guide Overview

Nexus CLI is organized into four domains, each handling a specific aspect of academic work:

## The Four Domains

### Knowledge Domain
Access and manage your Obsidian vault, search across notes, and visualize connections.

```bash
nexus knowledge vault search "mediation"
nexus knowledge vault graph --json
nexus knowledge search "topic" --all
```

### Research Domain
Query your Zotero library, extract text from PDFs, and manage literature.

```bash
nexus research zotero search "author:Smith"
nexus research pdf extract paper.pdf
nexus research zotero cite ABC123 --format bibtex
```

### Teaching Domain
Manage courses, build Quarto materials, and track teaching progress.

```bash
nexus teach course list
nexus teach quarto build slides.qmd
nexus teach course show stat-440
```

### Writing Domain
Track manuscripts, manage bibliographies, and work with LaTeX.

```bash
nexus write manuscript list
nexus write bib check manuscript-dir
nexus write manuscript show my-paper
```

## Getting Started

1. Install nexus: `pip install nexus-cli` or `uv pip install nexus-cli`
2. Run the health check: `nexus doctor`
3. Configure your paths: `nexus config`

## Common Workflows

### Finding Related Papers
```bash
# Search your Zotero library
nexus research zotero search "mediation analysis"

# Get BibTeX for a specific paper
nexus research zotero cite PAPERKEY --format bibtex
```

### Working with Your Vault
```bash
# Search notes
nexus knowledge vault search "project ideas"

# View connection graph
nexus knowledge vault graph

# Read a specific note
nexus knowledge vault read "10-PROJECTS/my-project.md"
```

### Managing Manuscripts
```bash
# List all manuscripts
nexus write manuscript list

# Check for citation issues
nexus write bib check my-manuscript
```

## JSON Output

All commands support `--json` for machine-readable output:

```bash
nexus research zotero search "topic" --json | jq '.[] | .title'
```

This makes it easy to pipe results to other tools or use with Claude.
