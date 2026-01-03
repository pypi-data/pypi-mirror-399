# Quick Start

Get up and running with Nexus in 5 minutes.

## 🎓 Recommended: Start with Interactive Tutorials

**The best way to learn Nexus is through interactive tutorials!**

```bash
# List available tutorials
nexus learn

# Start the Getting Started tutorial (7 steps, ~10 min)
nexus learn getting-started
```

The interactive tutorials will guide you through:
- ✅ Installation verification
- ✅ Configuration setup
- ✅ Basic commands
- ✅ Domain-specific workflows
- ✅ Advanced techniques

See [Tutorial Guide](../tutorials/tutorial-guide.md) for complete details.

---

## Manual Quick Start

Prefer to explore on your own? Follow these steps:

### Step 1: Verify Installation

```bash
# Check that nexus is installed
nexus --version

# Run health check
nexus doctor
```

## Step 2: Configure Paths

Create your configuration file:

```bash
# Open config in your editor
nexus config --edit
```

Minimal configuration (`~/.config/nexus/config.yaml`):

```yaml
vault:
  path: ~/Obsidian/MyVault

zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

pdf:
  directories:
    - ~/Documents/Research/PDFs

teaching:
  courses_dir: ~/projects/teaching

writing:
  manuscripts_dir: ~/projects/manuscripts
```

!!! tip
    You only need to configure the paths you'll use. Skip sections you don't need.

## Step 3: Try Basic Commands

### Search Your Vault

```bash
# Search for notes about "mediation"
nexus knowledge vault search "mediation"

# Get recent notes
nexus knowledge vault recent --limit 5
```

### Search Zotero

```bash
# Find papers about "causal inference"
nexus research zotero search "causal inference"

# Get recently added items
nexus research zotero recent
```

### Unified Search

```bash
# Search across ALL sources
nexus knowledge search "propensity score"
```

## Step 4: Explore Domains

Nexus has four main domains:

### 🧠 Knowledge

```bash
# Vault operations
nexus knowledge vault search "query"
nexus knowledge vault recent
nexus knowledge vault graph --stats

# Unified search
nexus knowledge search "query"
```

### 🔬 Research

```bash
# Zotero
nexus research zotero search "query"
nexus research zotero cite KEY

# PDFs
nexus research pdf search "query"
nexus research pdf extract paper.pdf
```

### 📚 Teaching

```bash
# Courses
nexus teach course list
nexus teach course show STAT-440

# Quarto
nexus teach quarto build
nexus teach quarto preview
```

### ✍️ Writing

```bash
# Manuscripts
nexus write manuscript list --active
nexus write manuscript show my-paper
nexus write manuscript stats

# Bibliography
nexus write bib check my-paper
```

## Step 5: Use JSON Output

All commands support `--json` for machine-readable output:

```bash
# Get JSON output
nexus knowledge vault search "mediation" --json

# Pipe to jq
nexus research zotero search "causal" --json | jq '.[0].title'

# Pipe to Claude
nexus knowledge search "methods" --json | claude -p "Summarize these results"
```

## Next Steps

### Recommended Learning Path

1. **Interactive Tutorials** (Best for new users)
   ```bash
   nexus learn getting-started  # Start here
   nexus learn medium           # Learn workflows
   nexus learn advanced         # Master techniques
   ```

2. **Read Documentation**
   - [User Guide](../guide/overview.md) - In-depth feature coverage
   - [CLI Reference](../reference/cli.md) - Complete command reference
   - [Tutorials](../tutorials/first-steps.md) - Step-by-step guides

3. **Set Up Integrations**
   - [MCP Server](../reference/mcp.md) - Claude Desktop integration
   - [Vault Setup](../tutorials/vault-setup.md) - Obsidian configuration
   - [Zotero Setup](../tutorials/zotero.md) - Literature management

## Common Workflows

### Literature Review

```bash
# Search Zotero
nexus research zotero search "mediation analysis" --limit 10

# Search PDFs
nexus research pdf search "indirect effects"

# Unified search
nexus knowledge search "mediation" > results.json
```

### Manuscript Writing

```bash
# Check citations
nexus write bib check my-paper

# Get manuscript stats
nexus write manuscript stats

# List active manuscripts
nexus write manuscript list --active
```

### Knowledge Management

```bash
# Search vault
nexus knowledge vault search "methods"

# Find orphaned notes
nexus knowledge vault orphans

# Generate graph
nexus knowledge vault graph --json > graph.json
```
