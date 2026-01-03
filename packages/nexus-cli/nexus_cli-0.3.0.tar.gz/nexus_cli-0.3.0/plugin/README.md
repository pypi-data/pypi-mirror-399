# Nexus CLI - Claude Code Plugin

A Claude Code plugin for the Nexus CLI knowledge workflow system. Provides skills and commands for research, teaching, and writing workflows.

## Overview

This plugin teaches Claude how to effectively use the `nexus` CLI for:

- **Knowledge Management**: Search Obsidian vault, find related notes, explore tags
- **Research**: Query Zotero library, extract PDF content, manage citations
- **Teaching**: Manage courses, build Quarto documents, track course progress
- **Writing**: Track manuscripts, check citations, manage bibliographies

## Installation

### Prerequisites

1. Install Nexus CLI:
   ```bash
   cd ~/projects/dev-tools/nexus-cli
   pip install -e .
   ```

2. Configure Nexus:
   ```bash
   nexus doctor  # Check configuration
   nexus config set knowledge.vault_dir ~/path/to/vault
   nexus config set research.zotero_db ~/Zotero/zotero.sqlite
   ```

### Install Plugin

Copy or symlink the plugin to your Claude plugins directory:

```bash
# Symlink (recommended for development)
ln -s ~/projects/dev-tools/nexus-cli/plugin ~/.claude/plugins/nexus-cli

# Or copy
cp -r ~/projects/dev-tools/nexus-cli/plugin ~/.claude/plugins/nexus-cli
```

## Skills

### Knowledge Domain
- **nexus-knowledge**: Vault operations, unified search, tag discovery

### Research Domain
- **nexus-research**: Zotero integration, PDF extraction, citation management

### Teaching Domain
- **nexus-teaching**: Course management, Quarto operations, lecture tracking

### Writing Domain
- **nexus-writing**: Manuscript tracking, bibliography management, citation checking

### Integration
- **nexus-integration**: Claude integration patterns, piping workflows, automation

## Slash Commands

| Command | Description |
|---------|-------------|
| `/nexus:dashboard` | Unified dashboard across all domains |
| `/nexus:manuscripts` | Show manuscript status and manage writing |
| `/nexus:search <query>` | Search across vault, Zotero, and manuscripts |
| `/nexus:cite <query>` | Quick citation lookup and formatting |
| `/nexus:check <manuscript>` | Check citations for issues |

## Usage Examples

### Via Claude

Ask Claude to use nexus:

```
"Search my vault for notes about mediation analysis"
"Show my active manuscripts"
"Find recent papers in my Zotero about bootstrap methods"
"Check citations in my collider paper"
```

### Piping to Claude

```bash
nexus knowledge search "causal inference" --json | claude -p "summarize these notes"
nexus write manuscript active --json | claude -p "which manuscript needs attention?"
```

### Direct CLI

```bash
nexus knowledge search "regression"
nexus research zotero recent --days 7
nexus write manuscript list
nexus teach course show stat-440
```

## Structure

```
plugin/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata
├── skills/
│   ├── knowledge/
│   │   └── vault-operations/skill.md
│   ├── research/
│   │   └── zotero-integration/skill.md
│   ├── teaching/
│   │   └── course-management/skill.md
│   ├── writing/
│   │   └── manuscript-management/skill.md
│   └── integration-patterns/skill.md
├── commands/
│   ├── dashboard.md
│   ├── manuscripts.md
│   ├── search.md
│   ├── cite.md
│   └── check.md
└── README.md
```

## License

MIT
