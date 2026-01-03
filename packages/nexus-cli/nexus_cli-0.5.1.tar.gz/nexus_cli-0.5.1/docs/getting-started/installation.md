# Installation

## Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Linux, or Windows
- **Optional**: Poppler utils for PDF extraction

## Installation Methods

### Method 1: From Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/Data-Wise/nexus-cli
cd nexus-cli

# Install with pip
pip install -e .

# Or install with uv (faster)
uv sync
```

### Method 2: With pip (when published)

```bash
# Install from PyPI
pip install nexus-cli

# Or with optional dependencies
pip install nexus-cli[docs]
```

### Method 3: Development Install

For development with all tools:

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Or with uv
uv sync --extra dev
```

## System Dependencies

### PDF Support

For PDF text extraction, install Poppler:

=== "macOS"
    ```bash
    brew install poppler
    ```

=== "Ubuntu/Debian"
    ```bash
    sudo apt-get install poppler-utils
    ```

=== "Fedora"
    ```bash
    sudo dnf install poppler-utils
    ```

### Verify Installation

Check that Nexus is installed correctly:

```bash
# Check version
nexus --version

# Run health check
nexus doctor
```

The `nexus doctor` command will verify:

- ✅ Python version
- ✅ System dependencies (pdftotext, quarto)
- ✅ Configuration file
- ✅ Vault/Zotero paths

## Next Steps

After installation, proceed to:

1. [Configuration](configuration.md) - Set up your paths
2. [Quick Start](quickstart.md) - Try your first commands
3. [User Guide](../guide/overview.md) - Learn about all features
