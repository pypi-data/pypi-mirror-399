---
name: nexus-research
description: Zotero integration, PDF extraction, and literature management
---

# Nexus Research Domain

**Zotero integration and literature management for academic research**

Use this skill when working on: searching literature, managing citations, extracting PDF content, exploring tags/collections, or building bibliographies.

---

## Command Reference

### Zotero Operations

```bash
# Search Zotero library
nexus research zotero search "mediation analysis"
nexus research zotero search "bootstrap" --limit 5

# Get specific item details
nexus research zotero get ITEM_KEY

# Generate citation
nexus research zotero cite ITEM_KEY
nexus research zotero cite ITEM_KEY --format bibtex

# Recent additions
nexus research zotero recent
nexus research zotero recent --days 30

# List all tags
nexus research zotero tags

# List all collections
nexus research zotero collections

# Get items by tag
nexus research zotero by-tag "mediation"
```

### PDF Operations

```bash
# Extract text from PDF
nexus research pdf extract /path/to/paper.pdf

# Get PDF metadata
nexus research pdf info /path/to/paper.pdf

# Search within PDFs
nexus research pdf search "keyword" /path/to/pdfs/
```

---

## Detailed Command Reference

### `nexus research zotero search`

Full-text search across Zotero library:

```bash
# Basic search (title, abstract, authors)
nexus research zotero search "bootstrap"

# Limit results
nexus research zotero search "mediation" --limit 10

# JSON output
nexus research zotero search "VanderWeele" --json
```

**Output fields:**
- `key` - Zotero item key
- `title` - Full title
- `authors` - Author list
- `year` - Publication year

### `nexus research zotero get`

Get full details for a specific item:

```bash
nexus research zotero get ABC123XY
nexus research zotero get ABC123XY --json
```

### `nexus research zotero cite`

Generate citations in various formats:

```bash
# APA format (default)
nexus research zotero cite ABC123XY

# BibTeX format
nexus research zotero cite ABC123XY --format bibtex

# Copy to clipboard (macOS)
nexus research zotero cite ABC123XY | pbcopy
```

### `nexus research zotero recent`

Find recently added/modified items:

```bash
# Last 7 days (default)
nexus research zotero recent

# Custom time range
nexus research zotero recent --days 30

# JSON output
nexus research zotero recent --json
```

### `nexus research zotero tags`

List all tags with counts:

```bash
nexus research zotero tags
nexus research zotero tags --json
```

### `nexus research zotero collections`

List all collections:

```bash
nexus research zotero collections
nexus research zotero collections --json
```

### `nexus research zotero by-tag`

Get items with a specific tag:

```bash
nexus research zotero by-tag "mediation"
nexus research zotero by-tag "sensitivity-analysis" --json
```

---

## Common Workflows

### Literature Review

```bash
# 1. Search for topic
nexus research zotero search "sensitivity analysis" --json > papers.json

# 2. Summarize with Claude
cat papers.json | claude -p "Group by methodology and summarize"

# 3. Export citations
nexus research zotero search "sensitivity" --json | \
  jq -r '.[].key' | \
  xargs -I {} nexus research zotero cite {} --format bibtex
```

### Building a Reading List

```bash
# Get recent papers
nexus research zotero recent --days 30 --json | \
  jq -r '.[] | "- [ ] \(.title) (\(.year))"'
```

### Tag Exploration

```bash
# Find popular tags
nexus research zotero tags --json | jq -r '.[] | "\(.count)\t\(.name)"' | sort -rn | head -10

# Get papers by tag
nexus research zotero by-tag "causal-inference" --json
```

---

## JSON Output Schema

```json
{
  "key": "ABC123XY",
  "title": "Introduction to Statistical Mediation Analysis",
  "authors": ["MacKinnon, D. P."],
  "date": "2008",
  "journal": "Lawrence Erlbaum Associates",
  "doi": "10.4324/9780203809556",
  "item_type": "book"
}
```

---

## Troubleshooting

### Zotero Database Not Found

```bash
# Check configuration
nexus doctor

# Verify Zotero path
ls ~/Zotero/zotero.sqlite
```

### Slow Searches

- Use `--limit` to cap results
- Use more specific queries
- Filter by tag: `nexus research zotero by-tag`

---

**Version**: 1.0.0
**Commands**: `nexus research zotero search|get|cite|recent|tags|collections|by-tag`, `nexus research pdf extract|info|search`
