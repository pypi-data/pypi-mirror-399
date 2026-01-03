---
name: nexus-integration
description: Claude integration patterns for Nexus CLI - piping, chaining, and automation
---

# Nexus Integration Patterns

**How Claude should work with Nexus CLI for maximum effectiveness**

Use this skill when: piping nexus output to Claude, building complex workflows, automating research tasks, or chaining commands together.

---

## Command Summary

```bash
# Knowledge
nexus knowledge search "query"
nexus knowledge vault search|read|write|daily|backlinks|recent|orphans|template

# Research
nexus research zotero search|get|cite|recent|tags|collections|by-tag
nexus research pdf extract|info|search

# Teaching
nexus teach course list|show|lectures|materials|syllabus
nexus teach quarto build|preview|info|clean|formats

# Writing
nexus write manuscript list|show|active|search|stats|deadlines
nexus write bib list|search|check|zotero

# System
nexus doctor
nexus config
```

---

## Integration Patterns

### Pattern 1: Claude Runs Nexus

Claude uses Bash tool to run nexus commands:

```bash
nexus knowledge search "mediation" --json
nexus write manuscript active --json
nexus research zotero search "bootstrap" --json
```

### Pattern 2: Piping to Claude

User pipes nexus output to Claude:

```bash
nexus knowledge search "causal inference" --json | claude -p "summarize"
nexus research zotero recent --json | claude -p "categorize by topic"
```

### Pattern 3: Chained Workflows

Complex multi-step workflows:

```bash
# Find missing citations, search Zotero
nexus write bib check ~/projects/research/paper --json | \
  jq -r '.missing[]' | \
  xargs -I {} nexus research zotero search "{}"
```

---

## Common Recipes

### Dashboard

```bash
echo "=== Manuscripts ===" && nexus write manuscript active
echo "=== Courses ===" && nexus teach course list
echo "=== Recent Zotero ===" && nexus research zotero recent --days 7
```

### Literature Review

```bash
# Search and summarize
nexus research zotero search "sensitivity" --json | \
  claude -p "Group by methodology"

# Export citations
nexus research zotero by-tag "mediation" --json | \
  jq -r '.[].key' | \
  xargs -I {} nexus research zotero cite {} --format bibtex
```

### Pre-Submission Check

```bash
nexus write manuscript show paper --json
nexus write bib check ~/projects/research/paper --json
```

### Course Prep

```bash
nexus teach course show stat-440
nexus teach course lectures stat-440
nexus teach quarto preview ~/projects/teaching/stat-440
```

---

## JSON Output

All commands support `--json`:

```bash
nexus write manuscript stats --json
nexus research zotero tags --json
nexus teach course list --json
```

### Using jq

```bash
# Extract fields
nexus research zotero search "topic" --json | jq -r '.[].title'

# Filter
nexus write manuscript list --json | jq '[.[] | select(.status == "active")]'

# Count
nexus research zotero tags --json | jq 'length'
```

---

## Best Practices

1. **Use `--json`** for reliable parsing
2. **Use `--limit`** for large result sets
3. **Check `nexus doctor`** if commands fail
4. **Chain with `&&`** for dependent commands

---

**Version**: 1.0.0
**Use with**: All nexus commands
