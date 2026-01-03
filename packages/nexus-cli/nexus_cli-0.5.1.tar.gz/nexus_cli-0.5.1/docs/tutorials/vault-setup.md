# Vault Setup Tutorial

This tutorial walks you through setting up and optimizing your Obsidian vault for use with Nexus CLI.

## Prerequisites

- Obsidian installed (or any markdown-based note system)
- Basic familiarity with markdown
- Nexus CLI installed

## Step 1: Choose Your Vault Location

Nexus can work with any directory containing markdown files, but works best with Obsidian vaults.

### Option A: Use an Existing Vault

If you already have an Obsidian vault:

```bash
# Point Nexus to your vault
nexus config
```

Edit the `vault.path` in `~/.config/nexus/config.yaml`:

```yaml
vault:
  path: /Users/username/Obsidian/MyVault
  templates: /Users/username/Obsidian/MyVault/templates
```

### Option B: Create a New Vault

```bash
# Create vault directory
mkdir -p ~/Obsidian/Nexus

# Initialize with sample structure
mkdir -p ~/Obsidian/Nexus/{Literature,Projects,Concepts,Templates}
```

Update config:

```yaml
vault:
  path: /Users/username/Obsidian/Nexus
  templates: /Users/username/Obsidian/Nexus/Templates
```

## Step 2: Verify Vault Configuration

Check that Nexus can access your vault:

```bash
nexus doctor
```

Look for:
```
Vault
  ✓ Vault path exists
  ✓ Vault readable
  ✓ Contains markdown files
```

## Step 3: Explore Your Vault

### List All Notes

```bash
nexus knowledge vault list
```

This shows all `.md` files in your vault (excluding system directories like `.obsidian`).

### Get Vault Statistics

```bash
nexus knowledge vault stats
```

Sample output:
```
Vault Statistics
─────────────────────────────────────

Total notes: 342
Total links: 1,247
Total tags: 89
Average links per note: 3.6

Most linked notes:
  1. Causal Inference (45 links)
  2. Mediation Analysis (32 links)
  3. Statistical Power (28 links)
```

### Read a Specific Note

```bash
nexus knowledge vault read "Note Title"

# Or with file extension
nexus knowledge vault read "concepts/mediation.md"
```

## Step 4: Understanding Links

Obsidian uses `[[WikiLinks]]` for internal links. Nexus understands these natively.

### Find Backlinks

See what notes link to a specific note:

```bash
nexus knowledge vault backlinks "Mediation Analysis"
```

Sample output:
```
Backlinks to 'Mediation Analysis'
─────────────────────────────────────

Found in 8 notes:
  • Projects/Current Research.md (3 links)
  • Literature/Baron Kenny 1986.md (2 links)
  • Concepts/Causal Inference.md (1 link)
  ...
```

### Find Orphan Notes

Notes with no incoming or outgoing links:

```bash
nexus knowledge vault orphans
```

## Step 5: Working with Tags

### Search by Tag

```bash
# Find all notes with a specific tag
nexus knowledge search "tag:statistics"

# Multiple tags
nexus knowledge search "tag:causal tag:inference"
```

### List All Tags

```bash
nexus knowledge vault tags
```

## Step 6: Graph Visualization

Generate graph data to visualize your vault's structure:

```bash
# Basic graph
nexus knowledge vault graph --json > vault-graph.json

# Include tags as nodes
nexus knowledge vault graph --tags --json > full-graph.json

# Limit to most connected nodes
nexus knowledge vault graph --limit 50 --json > core-graph.json
```

The JSON output can be visualized with tools like:
- [Obsidian Graph View](https://obsidian.md/)
- [Cytoscape](https://cytoscape.org/)
- [D3.js](https://d3js.org/)
- [vis.js](https://visjs.org/)

See [Graph Visualization Tutorial](graph-viz.md) for details.

## Step 7: Unified Search

Search across your entire vault:

```bash
# Simple search
nexus knowledge search "mediation"

# Case-sensitive
nexus knowledge search "Mediation" --case-sensitive

# Limit results
nexus knowledge search "statistics" --limit 10

# JSON output for processing
nexus knowledge search "causal" --json
```

## Best Practices

### 1. Use Consistent Naming

```markdown
<!-- Good: Clear, descriptive -->
[[Causal Inference]]
[[Baron and Kenny 1986]]

<!-- Avoid: Vague, generic -->
[[Notes]]
[[paper]]
```

### 2. Add Frontmatter

Enhance notes with YAML frontmatter:

```markdown
---
title: Mediation Analysis Overview
tags: [statistics, causal-inference, methods]
created: 2025-01-15
updated: 2025-12-25
status: active
---

# Mediation Analysis

Content here...
```

### 3. Create Templates

Save common note structures in `Templates/`:

```markdown
---
title: {{title}}
tags: [literature]
author: {{author}}
year: {{year}}
---

# {{title}}

## Summary

## Key Points

## Connections
```

### 4. Organize with Folders

```
vault/
├── Literature/        # Paper notes
├── Projects/          # Active research
├── Concepts/          # Conceptual notes
├── Methods/           # Statistical methods
├── Templates/         # Note templates
└── Archive/           # Completed/old notes
```

### 5. Use Descriptive Links

```markdown
<!-- Good: Contextual -->
See [[Causal Inference]] for background on counterfactuals.

<!-- Okay but less clear -->
See [[Causal Inference]].
```

## Advanced Features

### Create New Notes

```bash
# Create from template
nexus knowledge vault create "New Research Idea" --template research

# Quick create
echo "# Quick Note\n\nContent here" > ~/Obsidian/Nexus/quick-note.md
```

### Bulk Operations

```bash
# Find all notes modified in last 7 days
find ~/Obsidian/Nexus -name "*.md" -mtime -7

# Search and replace (be careful!)
nexus knowledge search "old term" --json | # process with jq or similar
```

### Integration with Zotero

Link literature notes to Zotero:

```markdown
---
title: Baron and Kenny 1986
zotero_key: baron1986moderator
---

# The moderator-mediator variable distinction

**Citation**: @baron1986moderator

## Summary
...
```

Then search both:

```bash
nexus knowledge search "baron" --source all
```

## Troubleshooting

### "No markdown files found"

Check that:
1. Vault path is correct: `nexus doctor`
2. Files have `.md` extension
3. Vault isn't empty

### "Permission denied"

```bash
# Check permissions
ls -la ~/Obsidian/Nexus

# Fix if needed
chmod -R u+rw ~/Obsidian/Nexus
```

### "Vault graph is empty"

Your notes might not have links yet. Start adding `[[WikiLinks]]` to connect ideas.

## Next Steps

- **Zotero Integration**: [Link your literature library](zotero.md)
- **Graph Visualization**: [Visualize connections](graph-viz.md)
- **Writing Workflow**: [Manage manuscripts](../guide/writing.md)

## Resources

- [Obsidian Help](https://help.obsidian.md/)
- [Zettelkasten Method](https://zettelkasten.de/introduction/)
- [Linking Your Thinking](https://www.linkingyourthinking.com/)
