# Nexus CLI

[![CI](https://github.com/Data-Wise/nexus-cli/workflows/CI/badge.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/ci.yml)
[![Tests](https://github.com/Data-Wise/nexus-cli/workflows/Tests/badge.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/test.yml)
[![Code Quality](https://github.com/Data-Wise/nexus-cli/workflows/Code%20Quality/badge.svg)](https://github.com/Data-Wise/nexus-cli/actions/workflows/quality.yml)
[![codecov](https://codecov.io/gh/Data-Wise/nexus-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/Data-Wise/nexus-cli)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/nexus-cli.svg)](https://badge.fury.io/py/nexus-cli)

> Knowledge workflow CLI for academic researchers

Nexus is a command-line interface that provides structured access to your research ecosystem without AI. It connects to Zotero, PDFs, Obsidian vaults, teaching materials, and manuscripts - letting you (or AI assistants) focus on thinking while Nexus handles data operations.

## Quick Start

```bash
# Install
pip install nexus-cli

# Health check
nexus doctor

# Search your knowledge
nexus knowledge search "mediation analysis"

# List manuscripts
nexus write manuscript list
```

See [Documentation](https://data-wise.github.io/nexus-cli) for full guide.

## Test Coverage

Current test coverage: **74.67%** (422 tests passing)

- CLI: 67.36%
- Knowledge/Vault: 78.06%
- Knowledge/Search: 80.00%
- Research/PDF: 79.51%
- Research/Zotero: 72.54%
- Teaching/Quarto: 91.36%
- Writing/Bibliography: 74.43%
- Writing/Manuscript: 83.38%

