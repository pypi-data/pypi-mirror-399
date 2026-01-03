# Knowledge Domain

The Knowledge domain provides access to your Obsidian vault and unified search capabilities.

## Vault Operations

### Searching Notes

```bash
# Basic search
nexus knowledge vault search "mediation"

# Limit results
nexus knowledge vault search "statistics" --limit 5

# JSON output for piping
nexus knowledge vault search "project" --json
```

### Reading Notes

```bash
# Read a specific note
nexus knowledge vault read "10-PROJECTS/my-project.md"

# Read by title (without path)
nexus knowledge vault read "my-project"
```

### Recent Notes

```bash
# Show last 10 modified notes
nexus knowledge vault recent

# Custom limit
nexus knowledge vault recent --limit 20
```

### Orphan Detection

Find notes with no incoming links:

```bash
nexus knowledge vault orphans
```

### Link Graph

Visualize connections between notes:

```bash
# Display graph summary
nexus knowledge vault graph

# JSON for visualization tools
nexus knowledge vault graph --json
```

## Unified Search

Search across all sources (vault, Zotero, PDFs):

```bash
# Search everything
nexus knowledge search "topic"

# Search specific source
nexus knowledge search "topic" --source vault
nexus knowledge search "topic" --source zotero
```

## Configuration

Configure vault path in `~/.config/nexus/config.yaml`:

```yaml
vault:
  path: ~/Obsidian/Nexus
  templates: ~/Obsidian/Nexus/_SYSTEM/templates
```
