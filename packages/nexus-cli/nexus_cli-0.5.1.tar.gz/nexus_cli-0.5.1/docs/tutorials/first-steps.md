# First Steps with Nexus CLI

Welcome to Nexus CLI! This guide will help you get started with the tool.

## 🎓 NEW: Interactive Tutorials

**The fastest way to learn Nexus is through our interactive tutorials!**

```bash
# List available tutorials
nexus learn

# Start the Getting Started tutorial (7 steps, ~10 min)
nexus learn getting-started

# Continue with intermediate workflows (11 steps, ~20 min)
nexus learn medium

# Master advanced techniques (12 steps, ~30 min)
nexus learn advanced
```

See [Tutorial Guide](tutorial-guide.md) for complete tutorial documentation.

## Manual First Steps

If you prefer to explore on your own, here's what to try:

### Prerequisites

Before starting, ensure you have:

- ✅ Nexus CLI installed (see [Installation Guide](../getting-started/installation.md))
- ✅ Configuration file created (see [Configuration Guide](../getting-started/configuration.md))
- ⚠️ At least one data source configured (Zotero, PDFs, or Obsidian vault)

## Step 1: Health Check

First, verify that Nexus is properly installed and configured:

```bash
nexus doctor
```

You should see output similar to:

```
Nexus CLI Health Check
─────────────────────────────────────

Version: 0.4.0
Python: 3.11+

Configuration
  ✓ Config file found
  ✓ Vault path configured
  ✓ Zotero database found

Dependencies
  ✓ pdftotext available
  ✓ sqlite3 available

All checks passed! ✅
```

!!! tip "Troubleshooting"
    If any checks fail, review the [Configuration Guide](../getting-started/configuration.md) to fix the issues.

## Step 2: Explore Your Data

### Option A: If You Have an Obsidian Vault

List all notes in your vault:

```bash
nexus knowledge vault list
```

Search for specific content:

```bash
nexus knowledge search "machine learning"
```

Get vault statistics:

```bash
nexus knowledge vault stats
```

### Option B: If You Have a Zotero Library

Search your Zotero library:

```bash
nexus research zotero search "causal inference" --limit 5
```

Get a citation:

```bash
nexus research zotero cite "smith2020"
```

List recent additions:

```bash
nexus research zotero recent --limit 10
```

### Option C: If You Have PDFs

List all PDFs:

```bash
nexus research pdf list
```

Search PDF contents:

```bash
nexus research pdf search "regression analysis"
```

Extract text from a specific PDF:

```bash
nexus research pdf extract paper.pdf --pages 1-5
```

## Step 3: Try JSON Output

Most commands support `--json` for machine-readable output, which is perfect for piping to other tools or Claude:

```bash
# Get vault graph as JSON
nexus knowledge vault graph --json > graph.json

# Search results as JSON
nexus knowledge search "mediation" --json

# Zotero search as JSON
nexus research zotero search "statistics" --json --limit 10
```

## Step 4: Explore the Help System

Nexus has comprehensive built-in help. Use `--help` at any level:

```bash
# Top-level help
nexus --help

# Domain help
nexus knowledge --help
nexus research --help
nexus teach --help
nexus write --help

# Command-specific help
nexus knowledge vault --help
nexus research zotero search --help
```

## Common Workflows

### Research Workflow

1. **Find papers on a topic**:
   ```bash
   nexus research zotero search "mediation analysis" --json
   ```

2. **Get citation for writing**:
   ```bash
   nexus research zotero cite "mackinnon2007"
   ```

3. **Search across PDFs**:
   ```bash
   nexus research pdf search "bootstrap confidence interval"
   ```

### Knowledge Management Workflow

1. **Search your notes**:
   ```bash
   nexus knowledge search "causal inference"
   ```

2. **Find backlinks to a note**:
   ```bash
   nexus knowledge vault backlinks "Mediation Analysis"
   ```

3. **Generate graph visualization**:
   ```bash
   nexus knowledge vault graph --json > graph.json
   ```

### Writing Workflow

1. **List your manuscripts**:
   ```bash
   nexus write manuscript list
   ```

2. **Check manuscript status**:
   ```bash
   nexus write manuscript status "my-paper"
   ```

3. **Verify bibliography**:
   ```bash
   nexus write bib check manuscript-dir/
   ```

## Tips for Success

!!! tip "Use Short Flags"
    Most options have short flags for faster typing:
    ```bash
    # These are equivalent
    nexus knowledge search "topic" --limit 10
    nexus knowledge search "topic" -n 10
    ```

!!! tip "Combine with Other Tools"
    Pipe Nexus output to other Unix tools:
    ```bash
    # Count matches
    nexus knowledge search "statistics" | wc -l
    
    # Save to file
    nexus research zotero recent --json > recent-papers.json
    
    # Pipe to Claude (if you have Claude CLI)
    nexus knowledge search "topic" --json | claude -p "Summarize these notes"
    ```

!!! tip "Check Versions"
    Keep Nexus updated:
    ```bash
    nexus --version
    git pull origin main  # If installed from source
    ```

## Next Steps

Now that you're familiar with the basics:

1. **Try the interactive tutorials** - `nexus learn getting-started`
2. **Set up your vault** - [Vault Setup Tutorial](vault-setup.md)
3. **Configure Zotero integration** - [Zotero Integration Tutorial](zotero.md)
4. **Visualize your knowledge graph** - [Graph Visualization Tutorial](graph-viz.md)
5. **Explore advanced features** - [User Guides](../guide/overview.md)

## Getting Help

- **Documentation**: [https://data-wise.github.io/nexus-cli](https://data-wise.github.io/nexus-cli)
- **Issues**: [GitHub Issues](https://github.com/Data-Wise/nexus-cli/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Data-Wise/nexus-cli/discussions)

Happy exploring! 🚀
