# Writing Domain

The Writing domain helps manage research manuscripts and bibliographies.

## Manuscript Management

### Listing Manuscripts

```bash
# List all manuscripts
nexus write manuscript list

# Filter by status
nexus write manuscript list --status draft

# JSON output
nexus write manuscript list --json
```

### Manuscript Details

```bash
nexus write manuscript show my-paper
```

## Bibliography Management

### Citation Checking

Find missing and unused citations:

```bash
nexus write bib check manuscript-dir/
```

Output shows:
- **Missing**: Citations in text but not in .bib file
- **Unused**: Entries in .bib file but not cited

### Bibliography Search

```bash
nexus write bib search "Smith 2024"
```

## Configuration

```yaml
writing:
  manuscripts_dir: ~/projects/research
  templates_dir: ~/templates/manuscripts
```

## Manuscript Directory Structure

```
my-paper/
├── .STATUS           # Manuscript status
├── _quarto.yml       # Quarto project config
├── index.qmd         # Main document
├── references.bib    # Bibliography
├── sections/
│   ├── introduction.qmd
│   └── methods.qmd
└── figures/
```

## Status File Format

The `.STATUS` file tracks manuscript progress:

```
status: draft
priority: 1
progress: 45
next: Complete methods section
target: JASA
```

## Supported Formats

- **Quarto**: `.qmd` files with `_quarto.yml`
- **LaTeX**: `.tex` files
- **Markdown**: Standard `.md` files

## Citation Formats

Supports standard citation formats:
- `[@Smith2024]` - Pandoc/Quarto style
- `\cite{Smith2024}` - LaTeX style
