# Research Domain

The Research domain integrates with Zotero and provides PDF text extraction.

## Zotero Integration

### Searching Papers

```bash
# Search by keyword
nexus research zotero search "mediation analysis"

# Filter by type
nexus research zotero search "statistics" --type journalArticle

# Filter by tag
nexus research zotero search "" --tag "to-read"

# JSON output
nexus research zotero search "topic" --json --limit 10
```

### Generating Citations

```bash
# APA format (default)
nexus research zotero cite ABC123

# BibTeX format
nexus research zotero cite ABC123 --format bibtex
```

### Recent Additions

```bash
nexus research zotero recent --limit 20
```

### Library Statistics

```bash
nexus research zotero stats
```

## PDF Operations

### Text Extraction

```bash
# Extract full text
nexus research pdf extract paper.pdf

# Extract specific pages
nexus research pdf extract paper.pdf --pages "1-5"

# Preserve layout
nexus research pdf extract paper.pdf --layout
```

### PDF Search

```bash
# Search across PDFs
nexus research pdf search "mediation"
```

## Configuration

```yaml
zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

pdf:
  directories:
    - ~/Documents/Research/PDFs
    - ~/Zotero/storage
```

## Requirements

- **Zotero**: Zotero database (zotero.sqlite)
- **pdftotext**: From Poppler (`brew install poppler`)
