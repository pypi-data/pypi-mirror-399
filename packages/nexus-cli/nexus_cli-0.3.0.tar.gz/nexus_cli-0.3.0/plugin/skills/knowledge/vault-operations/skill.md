---
name: nexus-knowledge
description: Obsidian vault operations and unified search across knowledge base
---

# Nexus Knowledge Domain

**Vault operations for Obsidian-based knowledge management**

Use this skill when working on: searching notes, finding related content, discovering backlinks, checking vault health, or navigating the user's Obsidian vault.

---

## Command Reference

### Unified Search

Search across all knowledge sources (vault + Zotero):

```bash
# Search everything
nexus knowledge search "mediation analysis"

# JSON output
nexus knowledge search "causal inference" --json

# Limit results
nexus knowledge search "regression" --limit 5
```

### Vault Operations

```bash
# Search vault notes
nexus knowledge vault search "topic"

# Read a specific note
nexus knowledge vault read "path/to/note.md"

# Write/update a note
nexus knowledge vault write "path/to/note.md" --content "..."

# Today's daily note
nexus knowledge vault daily

# Find notes linking to a note
nexus knowledge vault backlinks "path/to/note.md"

# Recently modified notes
nexus knowledge vault recent
nexus knowledge vault recent --limit 10

# Find orphan notes (no links)
nexus knowledge vault orphans

# Create from template
nexus knowledge vault template "template-name" "new-note.md"
```

---

## Detailed Command Reference

### `nexus knowledge search`

Unified search across vault and Zotero:

```bash
# Basic search
nexus knowledge search "bootstrap methods"

# JSON for piping
nexus knowledge search "sensitivity" --json

# Limit results
nexus knowledge search "mediation" --limit 10
```

**Output includes:**
- Source (vault or zotero)
- Title
- Snippet/excerpt
- Authors (for Zotero items)

### `nexus knowledge vault search`

Search only vault notes using ripgrep:

```bash
# Search vault
nexus knowledge vault search "causal inference"

# With context
nexus knowledge vault search "regression" --context 2
```

### `nexus knowledge vault recent`

Show recently modified notes:

```bash
# Last 10 (default)
nexus knowledge vault recent

# Custom limit
nexus knowledge vault recent --limit 20
```

### `nexus knowledge vault backlinks`

Find notes that link to a specific note:

```bash
nexus knowledge vault backlinks "Research_Lab/mediation-planning.md"
```

### `nexus knowledge vault orphans`

Find orphan notes (not linked from anywhere):

```bash
nexus knowledge vault orphans
```

---

## Common Patterns

### Piping to Claude

```bash
# Summarize search results
nexus knowledge search "mediation" --json | claude -p "summarize these findings"

# Analyze vault structure
nexus knowledge vault orphans --json | claude -p "categorize these orphan notes"
```

### Daily Workflow

```bash
# Open today's daily note
nexus knowledge vault daily

# Find what links to today's note
nexus knowledge vault backlinks "$(date +%Y-%m-%d).md"
```

### Research Discovery

```bash
# Find related notes
nexus knowledge vault search "sensitivity analysis"

# Cross-reference with Zotero
nexus knowledge search "sensitivity" --json | jq '.[] | select(.source == "zotero")'
```

---

## Vault Structure

The vault typically follows PARA organization:

| Folder | Purpose |
|--------|---------|
| `00-INBOX/` | Quick capture |
| `10-PROJECTS/` | Active work |
| `20-AREAS/` | Ongoing domains |
| `30-RESOURCES/` | Reference materials |
| `40-ARCHIVE/` | Completed work |
| `50-DAILY/` | Daily notes |
| `Research_Lab/` | Research projects |
| `Knowledge_Base/` | Permanent notes |

---

## Troubleshooting

### Vault Not Found

```bash
# Check configuration
nexus doctor

# View current config
nexus config
```

### Search Too Slow

For large vaults:
- Use `--limit` to cap results
- Use more specific search terms
- Search vault only: `nexus knowledge vault search`

---

**Version**: 1.0.0
**Commands**: `nexus knowledge search`, `nexus knowledge vault search|read|write|daily|backlinks|recent|orphans|template`
