# CLI Command Reference

Complete reference for all Nexus CLI commands.

## 🎓 New to Nexus?

**Start with interactive tutorials!**

```bash
nexus learn                    # Show all tutorials
nexus learn getting-started     # Begin learning
nexus learn medium              # Learn workflows
nexus learn advanced            # Master techniques
```

See [Tutorial Guide](../tutorials/tutorial-guide.md) and [Quick Reference](../tutorials/tutorial-quick-ref.md).

---

## Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show version and exit |
| `--help` | Show help and exit |

## Top-Level Commands

### `nexus doctor`
Run health checks on your Nexus configuration.

```bash
nexus doctor
```

Checks:
- Configuration file existence
- Vault accessibility
- Zotero database connection
- Required tools (pdftotext, quarto)

### `nexus config`
Display current configuration.

```bash
nexus config
```

### `nexus learn`
Interactive learning tutorials.

```bash
nexus learn                            # List available tutorials
nexus learn <level>                     # Run a tutorial
nexus learn <level> --step N            # Resume from step N
```

**Levels:**
- `getting-started` - Basic commands and setup (7 steps, ~10 min)
- `medium` - Domain workflows (11 steps, ~20 min)
- `advanced` - Batch operations and integrations (12 steps, ~30 min)

See [Tutorial Quick Reference](../tutorials/tutorial-quick-ref.md) for details.

---

## Knowledge Domain

### `nexus knowledge vault search`
Search notes in your Obsidian vault.

```bash
nexus knowledge vault search QUERY [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Maximum results (default: 20) |
| `--json` | Output as JSON |

### `nexus knowledge vault read`
Read a note from the vault.

```bash
nexus knowledge vault read PATH
```

### `nexus knowledge vault graph`
Generate a link graph of your vault.

```bash
nexus knowledge vault graph [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON |
| `--format` | Output format (json, dot) |

### `nexus knowledge vault recent`
Show recently modified notes.

```bash
nexus knowledge vault recent [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Number of notes (default: 10) |
| `--json` | Output as JSON |

### `nexus knowledge vault orphans`
Find notes with no incoming links.

```bash
nexus knowledge vault orphans [OPTIONS]
```

### `nexus knowledge search`
Unified search across all sources.

```bash
nexus knowledge search QUERY [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source` | Source to search (vault, zotero, pdf, all) |
| `--limit, -n` | Maximum results |
| `--json` | Output as JSON |

---

## Research Domain

### `nexus research zotero search`
Search your Zotero library.

```bash
nexus research zotero search QUERY [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--limit, -n` | Maximum results (default: 20) |
| `--type` | Filter by item type |
| `--tag` | Filter by tag |
| `--json` | Output as JSON |

### `nexus research zotero cite`
Generate a citation for an item.

```bash
nexus research zotero cite KEY [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--format, -f` | Citation format (apa, bibtex) |

### `nexus research zotero recent`
Show recently added items.

```bash
nexus research zotero recent [OPTIONS]
```

### `nexus research zotero stats`
Show library statistics.

```bash
nexus research zotero stats
```

### `nexus research pdf extract`
Extract text from a PDF.

```bash
nexus research pdf extract PATH [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--pages` | Page range (e.g., "1-5") |
| `--layout` | Preserve layout |

### `nexus research pdf search`
Search across PDFs.

```bash
nexus research pdf search QUERY [OPTIONS]
```

---

## Teaching Domain

### `nexus teach course list`
List all courses.

```bash
nexus teach course list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--active` | Show only active courses |
| `--json` | Output as JSON |

### `nexus teach course show`
Show course details.

```bash
nexus teach course show NAME
```

### `nexus teach quarto build`
Build Quarto documents.

```bash
nexus teach quarto build PATH [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--format, -f` | Output format (html, pdf, revealjs) |

### `nexus teach quarto preview`
Start preview server.

```bash
nexus teach quarto preview PATH [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--port` | Server port (default: 4200) |

---

## Writing Domain

### `nexus write manuscript list`
List all manuscripts.

```bash
nexus write manuscript list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--status` | Filter by status |
| `--json` | Output as JSON |

### `nexus write manuscript show`
Show manuscript details.

```bash
nexus write manuscript show NAME
```

### `nexus write bib check`
Check citations in a manuscript.

```bash
nexus write bib check PATH
```

Reports:
- Missing citations (cited but not in .bib)
- Unused entries (in .bib but not cited)

### `nexus write bib search`
Search bibliography entries.

```bash
nexus write bib search QUERY [OPTIONS]
```
