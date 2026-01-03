# Nexus Tutorial Quick Reference

## Commands

```bash
nexus learn                    # Show all tutorials
nexus learn getting-started     # Start beginner tutorial
nexus learn medium              # Start intermediate tutorial
nexus learn advanced            # Start advanced tutorial
nexus learn <level> --step N    # Resume from step N
nexus learn --help                  # Show help
```

## Tutorial Levels

| Level | Steps | Duration | Focus |
|-------|-------|----------|-------|
| **Getting Started** | 7 | 10-15 min | Basics, configuration, first commands |
| **Medium** | 11 | 20-30 min | Research, teaching, writing workflows |
| **Advanced** | 12 | 30-40 min | Batch ops, integrations, automation |

## Getting Started Tutorial (7 steps)

1. **Welcome to Nexus** - Overview and philosophy
2. **Check Installation** - `nexus doctor`
3. **View Configuration** - `nexus config`
4. **Explore Commands** - `nexus --help`
5. **First Search** - `nexus research zotero search`
6. **JSON Output** - `--json` flag usage
7. **Next Steps** - Where to go from here

**Start:** `nexus learn getting-started`

## Medium Tutorial (11 steps)

### Research Workflow (4 steps)
1. Literature discovery - Search Zotero by topic
2. Paper details - Get full metadata
3. Citations - Generate APA/BibTeX
4. Tags - Explore and filter

### Knowledge Workflow (3 steps)
5. Vault search - Find notes
6. Reading notes - Parse frontmatter
7. Graph analysis - Statistics and connections

### Other Workflows (4 steps)
8. Teaching - Course overview
9. Writing - Manuscript tracking
10. Unified search - Cross-domain queries
11. Completion - Summary and next steps

**Start:** `nexus learn medium`

## Advanced Tutorial (12 steps)

### Batch Operations (3 steps)
1. Introduction - Advanced overview
2. Status updates - Bulk manuscript updates
3. Progress tracking - Multiple manuscripts
4. Metadata export - JSON/CSV output

### Graph Visualization (2 steps)
5. GraphML export - For Gephi/Cytoscape
6. D3.js export - Web visualizations

### Integration & Automation (5 steps)
7. JSON pipelines - Claude integration
8. Citation checking - Bibliography validation
9. Quarto automation - Build projects
10. Dependencies - Dependency checking
11. Custom workflows - Build your own
12. Completion - Expert summary

**Start:** `nexus learn advanced`

## Key Features

- ✅ **Interactive** - Hands-on command practice
- ✅ **Progressive** - Build skills step-by-step
- ✅ **Pausable** - Resume with `--step N`
- ✅ **Self-paced** - No time pressure
- ✅ **Real-world** - Actual commands, not examples
- ✅ **Hints** - Contextual help at each step

## Learning Path

```
┌─────────────────────────────────────────────┐
│  NEW USER                                   │
│  ↓                                          │
│  nexus learn getting-started         │
│  (Learn basics, 10 min)                     │
│  ↓                                          │
│  nexus learn medium                  │
│  (Master workflows, 20 min)                 │
│  ↓                                          │
│  nexus learn advanced                │
│  (Power user, 30 min)                       │
│  ↓                                          │
│  EXPERT USER                                │
└─────────────────────────────────────────────┘
```

## Common Use Cases

### First Time User
```bash
# Start from the beginning
nexus learn getting-started
```

### Skip to Workflows
```bash
# Already know basics? Jump to workflows
nexus learn medium
```

### Learn Advanced Features
```bash
# Ready for batch operations?
nexus learn advanced
```

### Resume After Break
```bash
# Paused at step 5? Resume here
nexus learn medium --step 5
```

### Review Specific Topic
```bash
# Re-run just the steps you need
nexus learn advanced --step 7
```

## Commands Covered

### Getting Started
- `nexus doctor`
- `nexus config`
- `nexus --help`
- `nexus research zotero search`
- `--json` flag

### Medium
- `nexus research zotero search|get|cite|tags|by-tag`
- `nexus knowledge vault search|read|graph`
- `nexus teach course list`
- `nexus write manuscript list`
- `nexus knowledge search`

### Advanced
- `nexus write manuscript batch-status|batch-progress|export`
- `nexus knowledge vault export graphml|d3|json`
- `nexus write bib check`
- `nexus teach quarto build|info`
- JSON pipeline patterns

## Tips

### Before Starting
- ✅ Install Nexus: `nexus --version`
- ✅ Check health: `nexus doctor`
- ✅ Have terminal ready
- ✅ Set aside time (10-40 min)

### During Tutorial
- ✅ Actually run commands
- ✅ Experiment with variations
- ✅ Take notes
- ✅ Don't rush

### After Tutorial
- ✅ Practice regularly
- ✅ Build custom scripts
- ✅ Integrate with Claude
- ✅ Share feedback

## Troubleshooting

**Tutorial won't start?**
- Check: `nexus --version` works
- Verify: `nexus learn` shows tutorials
- Use correct level name: `getting-started`, `medium`, `advanced`

**Commands fail?**
- Run: `nexus doctor` to check components
- Some commands need Zotero/vault configured
- Tutorial explains patterns even if data missing

**Want to skip?**
- Use: `--step N` to jump ahead
- Jump between tutorials freely
- No prerequisites (except Getting Started recommended first)

## Getting Help

- **Inline help**: `nexus learn --help`
- **Full guide**: `TUTORIAL_GUIDE.md`
- **Documentation**: https://data-wise.github.io/nexus-cli
- **Issues**: https://github.com/Data-Wise/nexus-cli/issues

## Quick Examples

```bash
# List what's available
nexus learn

# Start learning (recommended)
nexus learn getting-started

# Jump to workflows
nexus learn medium

# Master advanced features
nexus learn advanced

# Resume from step 8
nexus learn medium --step 8

# Get help anytime
nexus learn --help
```

---

**Ready to learn?** 🎓

```bash
nexus learn getting-started
```
