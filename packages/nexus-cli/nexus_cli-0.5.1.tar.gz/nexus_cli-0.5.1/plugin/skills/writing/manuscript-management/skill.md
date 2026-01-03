---
name: nexus-writing
description: Manuscript tracking, bibliography management, and academic writing workflows
---

# Nexus Writing Domain

**Manuscript tracking and bibliography management for academic writing**

Use this skill when working on: tracking manuscripts, managing citations, checking bibliography, or coordinating writing projects.

---

## Command Reference

### Manuscript Operations

```bash
# List all manuscripts
nexus write manuscript list
nexus write manuscript list --all  # Include archived

# Show manuscript details
nexus write manuscript show MANUSCRIPT_NAME

# List active manuscripts
nexus write manuscript active

# Search manuscripts
nexus write manuscript search "mediation"

# Get statistics
nexus write manuscript stats

# View deadlines
nexus write manuscript deadlines
```

### Bibliography Operations

```bash
# List bibliography entries
nexus write bib list MANUSCRIPT_PATH

# Search bibliography
nexus write bib search MANUSCRIPT_PATH "author_name"

# Check citations (find missing/unused)
nexus write bib check MANUSCRIPT_PATH

# Search Zotero for references
nexus write bib zotero "search_query"
```

---

## Detailed Command Reference

### `nexus write manuscript list`

List all manuscripts with status:

```bash
# Active manuscripts (excludes archived/complete)
nexus write manuscript list

# Include all
nexus write manuscript list --all

# JSON output
nexus write manuscript list --json
```

**Output:**
- Status emoji
- Name
- Progress bar
- Word count
- Target journal
- Next action

### `nexus write manuscript show`

Detailed manuscript view:

```bash
nexus write manuscript show collider
nexus write manuscript show collider --json
```

**Shows:**
- Title and authors
- Status and progress
- Format (Quarto, LaTeX, Markdown)
- Word count
- Target venue
- Next action

### `nexus write manuscript active`

List actively worked manuscripts:

```bash
nexus write manuscript active
nexus write manuscript active --json
```

### `nexus write manuscript search`

Search by name or title:

```bash
nexus write manuscript search "mediation"
```

### `nexus write manuscript stats`

Aggregate statistics:

```bash
nexus write manuscript stats
nexus write manuscript stats --json
```

**Shows:**
- Total count
- By status
- By format
- Total words

### `nexus write manuscript deadlines`

Show manuscripts with targets:

```bash
nexus write manuscript deadlines
```

---

## Bibliography Commands

### `nexus write bib list`

List all bibliography entries:

```bash
nexus write bib list ~/projects/research/collider
nexus write bib list ~/projects/research/collider --json
```

### `nexus write bib search`

Search within bibliography:

```bash
nexus write bib search ~/projects/research/collider "VanderWeele"
```

### `nexus write bib check`

Check for citation problems:

```bash
nexus write bib check ~/projects/research/collider
nexus write bib check ~/projects/research/collider --json
```

**Checks for:**
- Missing citations (cited but not in .bib)
- Unused entries (in .bib but not cited)
- Citation count

**Detects formats:**
- Pandoc/Quarto: `@key`, `[@key]`
- LaTeX: `\cite{key}`, `\citep{key}`

### `nexus write bib zotero`

Search Zotero for references:

```bash
nexus write bib zotero "sensitivity analysis"
nexus write bib zotero "bootstrap" --limit 5
```

---

## Manuscript Directory Structure

```
manuscript-name/
├── .STATUS                 # Status (required)
├── _quarto.yml             # Quarto config
├── _manuscript/
│   └── index.qmd           # Main article
├── references.bib          # Bibliography
└── _output/                # Built outputs
```

### .STATUS File Format

```yaml
status: draft
priority: 2
progress: 45
next: Revise Methods section
type: research
target: JASA
```

---

## Status Emojis

| Status | Emoji |
|--------|-------|
| idea | 💡 |
| planning | 📋 |
| active | 🔥 |
| draft | 📝 |
| revision | ✏️ |
| under review | 📬 |
| complete | ✅ |
| paused | ⏸️ |

---

## Common Workflows

### Pre-Submission Check

```bash
# Check status
nexus write manuscript show my-paper

# Verify citations
nexus write bib check ~/projects/research/my-paper

# Word count
nexus write manuscript show my-paper --json | jq '.word_count'
```

### Find Missing References

```bash
# Get missing citations
nexus write bib check ~/projects/research/paper --json | \
  jq -r '.missing[]' | \
  xargs -I {} nexus research zotero search "{}"
```

### Manuscript Dashboard

```bash
nexus write manuscript active --json | \
  jq -r '.[] | "\(.status_emoji) \(.name): \(.progress)%"'
```

---

## Troubleshooting

### Manuscripts Not Found

```bash
nexus doctor
nexus config
```

### Citation Check Issues

- Ensure `.bib` files are in manuscript folder
- Keys are case-sensitive
- Check for typos in citation keys

---

**Version**: 1.0.0
**Commands**: `nexus write manuscript list|show|active|search|stats|deadlines`, `nexus write bib list|search|check|zotero`
