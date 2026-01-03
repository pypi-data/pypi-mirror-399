# Configuration

Nexus uses a YAML configuration file at `~/.config/nexus/config.yaml`.

## Configuration File Location

Default path: `~/.config/nexus/config.yaml`

View or edit your configuration:

```bash
# View current configuration
nexus config

# Edit in your $EDITOR
nexus config --edit
```

## Complete Configuration Reference

```yaml
# Obsidian Vault Configuration
vault:
  path: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault
  templates: ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault/_SYSTEM/templates

# Zotero Configuration  
zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

# PDF Directories
pdf:
  directories:
    - ~/Documents/Research/PDFs
    - ~/Documents/Teaching/PDFs
    - ~/Downloads

# Teaching Configuration
teaching:
  courses_dir: ~/projects/teaching

# Writing Configuration
writing:
  manuscripts_dir: ~/projects/quarto/manuscripts
```

## Configuration by Domain

### Knowledge Domain

```yaml
vault:
  path: ~/Obsidian/MyVault              # Required
  templates: ~/Obsidian/MyVault/_SYSTEM/templates  # Optional
```

**vault.path**: Path to your Obsidian vault root directory
**vault.templates**: Path to templates folder for `nexus knowledge vault template`

### Research Domain

#### Zotero

```yaml
zotero:
  database: ~/Zotero/zotero.sqlite    # Required
  storage: ~/Zotero/storage           # Optional
```

**zotero.database**: Path to Zotero SQLite database
**zotero.storage**: Path to Zotero storage folder (for PDF access)

#### PDFs

```yaml
pdf:
  directories:                          # Optional
    - ~/Documents/Research/PDFs
    - ~/Documents/Teaching/PDFs
```

**pdf.directories**: List of directories to search for PDFs

### Teaching Domain

```yaml
teaching:
  courses_dir: ~/projects/teaching    # Required for teaching commands
```

**teaching.courses_dir**: Parent directory containing course folders

### Writing Domain

```yaml
writing:
  manuscripts_dir: ~/projects/manuscripts  # Required for writing commands
```

**writing.manuscripts_dir**: Parent directory containing manuscript folders

## Path Expansion

Nexus supports:

- **Tilde expansion**: `~/path` → `/Users/username/path`
- **Environment variables**: `$HOME/path`
- **Relative paths**: Resolved from current directory

## Validation

Verify your configuration:

```bash
nexus doctor
```

This checks:

- Configuration file exists
- All configured paths exist
- System dependencies are available
- Python version is compatible

## Example Configurations

### Minimal (Vault Only)

```yaml
vault:
  path: ~/Obsidian/MyVault
```

### Research Focus

```yaml
vault:
  path: ~/Obsidian/Research

zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

pdf:
  directories:
    - ~/Documents/PDFs
    - ~/Downloads

writing:
  manuscripts_dir: ~/Documents/Manuscripts
```

### Academic Complete

```yaml
vault:
  path: ~/Obsidian/Academic
  templates: ~/Obsidian/Academic/.templates

zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

pdf:
  directories:
    - ~/Documents/Research/PDFs
    - ~/Documents/Teaching/PDFs

teaching:
  courses_dir: ~/Teaching

writing:
  manuscripts_dir: ~/Research/Manuscripts
```

## Troubleshooting

### Configuration file not found

```bash
# Create default configuration
mkdir -p ~/.config/nexus
nexus config > ~/.config/nexus/config.yaml
```

### Path doesn't exist

Check that paths exist:

```bash
# On macOS/Linux
ls -la ~/Obsidian/MyVault
ls -la ~/Zotero/zotero.sqlite
```

### Permission denied

Ensure Nexus can read your files:

```bash
chmod -R u+r ~/Obsidian/MyVault
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Try your first commands
- [User Guide](../guide/overview.md) - Learn about all features
