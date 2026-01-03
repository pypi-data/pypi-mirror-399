# Nexus CLI v0.5.0 Release Notes

**Release Date**: December 25, 2025

🎨 **Feature Enhancement Release** - Nexus CLI adds powerful graph export capabilities and batch manuscript operations for improved productivity!

## 🚀 Highlights

This release focuses on **user productivity** and **workflow efficiency**, adding two major feature areas that enhance Nexus CLI's capabilities for knowledge management and manuscript tracking.

### Key Achievements

- **✅ 302 Tests** (up from 275) with **54% coverage** (up from 50%)
- **📊 Graph Export Formats** (GraphML, D3.js, JSON)
- **📝 Batch Manuscript Operations** (status, progress, archiving)
- **📚 Comprehensive Documentation** (tutorials, API reference, architecture)
- **🎯 27% Coverage Boost** for manuscript module (50% → 78%)

## 📦 What's New

### 1. Graph Export Formats

Export your Obsidian vault knowledge graph to multiple formats for visualization and analysis.

#### New Export Formats

**GraphML Format** (for Gephi, Cytoscape, yEd):
```bash
nexus knowledge vault export graphml graph.graphml
nexus knowledge vault export graphml graph.graphml --tags
nexus knowledge vault export graphml graph.graphml --limit 100
```

**D3.js Format** (for web visualizations):
```bash
nexus knowledge vault export d3 graph.json
nexus knowledge vault export d3 graph.json --tags
```

**JSON Format** (existing, now with same options):
```bash
nexus knowledge vault export json graph.json --tags --limit 100
```

#### Features

- **Tag Support**: Include tags as nodes with `--tags` flag
- **Node Limiting**: Limit output size with `--limit N` for large vaults
- **Proper XML Escaping**: Safe handling of special characters in GraphML
- **D3.js Compatible**: Direct use in Observable, D3 visualizations
- **Network Analysis Ready**: Import into Gephi, Cytoscape for analysis

#### Implementation Details

New methods in `VaultManager` class (`nexus/knowledge/vault.py:319`):

```python
def export_graphml(output_path, include_tags=False, limit=None):
    """Export vault graph to GraphML format."""
    
def export_d3(output_path, include_tags=False, limit=None):
    """Export vault graph to D3.js-compatible JSON."""
    
def _escape_xml(text):
    """Escape XML special characters."""
```

### 2. Batch Manuscript Operations

Manage multiple manuscripts efficiently with new batch operations.

#### Batch Status Updates

Update status for multiple manuscripts at once:

```bash
# Update multiple manuscripts to "review"
nexus write manuscript batch-status paper1 paper2 paper3 --status review

# Move manuscripts to "published"
nexus write manuscript batch-status paper1 paper2 --status published
```

#### Batch Progress Updates

Update progress for multiple manuscripts:

```bash
# Update progress for multiple papers
nexus write manuscript batch-progress paper1:75 paper2:90 paper3:50

# Quick update all to same progress
nexus write manuscript batch-progress paper1:100 paper2:100 --status published
```

#### Batch Archive

Archive old manuscripts by moving to Archive/ subdirectory:

```bash
# Archive completed papers
nexus write manuscript batch-archive old-paper1 old-paper2

# Automatically creates Archive/ directory if needed
# Moves .STATUS files and maintains metadata
```

#### Metadata Export

Export all manuscript metadata to JSON or CSV:

```bash
# Export to JSON
nexus write manuscript export manuscripts.json

# Export to CSV for Excel/spreadsheet use
nexus write manuscript export manuscripts.csv --format csv
```

#### Features

- **Atomic Operations**: All-or-nothing updates for data integrity
- **Error Reporting**: Detailed success/failure reporting per manuscript
- **Automatic Directory Creation**: Creates Archive/ subdirectory as needed
- **Status File Creation**: Creates .STATUS files for manuscripts without them
- **Flexible Export**: JSON or CSV formats for metadata export

#### Implementation Details

New methods in `ManuscriptManager` class (`nexus/writing/manuscript.py:355`):

```python
def batch_update_status(manuscripts: list[str], new_status: str) -> dict:
    """Update status for multiple manuscripts."""
    
def batch_update_progress(updates: dict[str, int]) -> dict:
    """Update progress for multiple manuscripts."""
    
def batch_archive(manuscripts: list[str]) -> dict:
    """Archive manuscripts to Archive/ subdirectory."""
    
def batch_export_metadata(output_path: Path, format: str = "json") -> None:
    """Export metadata to JSON or CSV."""
```

### 3. Comprehensive Documentation

Added extensive documentation covering tutorials, API reference, and architecture.

#### New Tutorial Pages (~4,900 lines)

1. **First Steps** (`docs/tutorials/first-steps.md`)
   - Complete getting started guide
   - Domain-specific workflows
   - Integration patterns

2. **Vault Setup** (`docs/tutorials/vault-setup.md`)
   - Obsidian vault configuration
   - Graph visualization setup
   - Search optimization

3. **Zotero Integration** (`docs/tutorials/zotero.md`)
   - Literature database setup
   - Search workflows
   - Citation management

4. **Graph Visualization** (`docs/tutorials/graph-viz.md`)
   - Export format guide
   - NetworkX, D3.js, Pyvis examples
   - Advanced graph analysis

#### New Reference Pages (~2,200 lines)

1. **Python API Reference** (`docs/reference/api.md`)
   - Complete class and method documentation
   - Code examples for all modules
   - Integration patterns

2. **MCP Server Reference** (`docs/reference/mcp.md`)
   - 17 MCP tools documented
   - Usage examples
   - Integration with Claude Desktop/CLI

#### New Development Docs (~2,400 lines)

1. **Testing Guide** (`docs/development/testing.md`)
   - Test suite overview (302 tests)
   - Coverage reports (54%)
   - Writing new tests

2. **Architecture Documentation** (`docs/development/architecture.md`)
   - System design
   - Module organization
   - Extension patterns

## 📊 Statistics

### Test Metrics

- **Total Tests**: 302 (up from 275, +27 tests, **+9.8%**)
- **Passing Tests**: 301/302 (99.7% pass rate)
- **Code Coverage**: 54.35% (up from 49.88%, **+4.47%**)
- **Lines of Test Code**: ~5,200 lines
- **Test Files**: 18 test modules

### Module Coverage Improvements

| Module | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Overall** | 49.88% | 54.35% | **+4.47%** |
| `writing/manuscript.py` | 50.99% | 78.03% | **+27.04%** 🎯 |
| `knowledge/vault.py` | 53.69% | 59.28% | **+5.59%** |
| `teaching/quarto.py` | 87.62% | 91.36% | **+3.74%** |

### Documentation

- **Tutorial Pages**: 4 new pages (~4,900 lines)
- **Reference Pages**: 2 new pages (~2,200 lines)
- **Development Pages**: 2 new pages (~2,400 lines)
- **Total Documentation**: ~9,500 lines of comprehensive guides

### New Test Files

1. **`test_graph_export.py`** (11 tests)
   - GraphML export with/without tags
   - D3.js export with/without tags
   - Limit functionality
   - Empty vault handling
   - XML escaping

2. **`test_manuscript_batch.py`** (16 tests)
   - Batch status updates
   - Batch progress updates
   - Batch archiving
   - Metadata export (JSON/CSV)
   - Error handling
   - Integration workflows

## 🔧 Technical Details

### New Commands

#### Knowledge Domain
```bash
nexus knowledge vault export graphml <output> [--tags] [--limit N]
nexus knowledge vault export d3 <output> [--tags] [--limit N]
```

#### Writing Domain
```bash
nexus write manuscript batch-status <papers...> --status <status>
nexus write manuscript batch-progress <paper:progress...>
nexus write manuscript batch-archive <papers...>
nexus write manuscript export <output> [--format json|csv]
```

### API Changes

**New Public Methods**:

```python
# VaultManager (nexus/knowledge/vault.py)
vault.export_graphml(output_path, include_tags, limit)
vault.export_d3(output_path, include_tags, limit)

# ManuscriptManager (nexus/writing/manuscript.py)
manager.batch_update_status(manuscripts, new_status)
manager.batch_update_progress(updates)
manager.batch_archive(manuscripts)
manager.batch_export_metadata(output_path, format)
```

### Return Value Format

All batch operations return a consistent dictionary:

```python
{
    "success": ["paper1", "paper2"],
    "failed": ["paper3"],
    "errors": {"paper3": "Error message"}
}
```

## 📚 Documentation Links

- **Documentation Site**: https://data-wise.github.io/nexus-cli
- **Tutorials**: https://data-wise.github.io/nexus-cli/tutorials/
- **API Reference**: https://data-wise.github.io/nexus-cli/reference/api/
- **Architecture**: https://data-wise.github.io/nexus-cli/development/architecture/
- **Changelog**: https://data-wise.github.io/nexus-cli/changelog/

## 🎯 Migration Guide

### From v0.4.0 to v0.5.0

**No breaking changes!** This is a fully backward-compatible release.

All existing commands, configuration, and workflows continue to work exactly as before.

### What's New

The new features are **additive only**:

- New export formats for knowledge graphs
- New batch operations for manuscripts
- Enhanced documentation
- More comprehensive test coverage

### Recommended Actions

1. **Try the new graph export formats**:
   ```bash
   nexus knowledge vault export graphml my-vault.graphml --tags
   ```

2. **Use batch operations for manuscript management**:
   ```bash
   nexus write manuscript batch-status paper1 paper2 --status review
   ```

3. **Explore the new documentation**:
   - Read the tutorials for workflow ideas
   - Check the API reference for programmatic use
   - Review architecture docs for extension patterns

## 🔮 What's Next

Looking ahead to future releases:

### Planned for v0.6.0
- [ ] Additional graph export formats (GML, Cytoscape JSON)
- [ ] Batch operations for other domains (courses, bibliography)
- [ ] Interactive CLI mode with prompts
- [ ] Performance benchmarks and optimization

### Under Consideration
- [ ] Web UI for graph visualization
- [ ] Workflow automation commands
- [ ] Plugin system for custom exporters
- [ ] API client library for programmatic access
- [ ] Export to graph databases (Neo4j, ArangoDB)

## 🎓 Use Cases

### Graph Visualization Workflow

```bash
# Export vault graph to GraphML
nexus knowledge vault export graphml vault.graphml --tags

# Import to Gephi/Cytoscape for visual analysis
# - Community detection
# - Centrality analysis
# - Network statistics

# Export to D3.js for web visualization
nexus knowledge vault export d3 vault.json

# Use in Observable notebooks or custom visualizations
```

### Manuscript Management Workflow

```bash
# Weekly review: update all manuscript progress
nexus write manuscript batch-progress \
  paper1:85 \
  paper2:60 \
  paper3:95

# Move to review status
nexus write manuscript batch-status paper3 --status review

# Archive completed papers
nexus write manuscript batch-archive old-paper1 old-paper2

# Export metadata for reporting
nexus write manuscript export manuscripts.csv --format csv
```

## 🙏 Acknowledgments

Special thanks to:

- Claude Code for development assistance
- Users requesting graph export features
- The Obsidian community for inspiration
- NetworkX and D3.js communities

## 📝 Full Changelog

For a complete list of changes, see the [Changelog](https://data-wise.github.io/nexus-cli/changelog/).

## 🐛 Known Issues

None reported at this time.

If you encounter any issues, please report them on our [GitHub Issues](https://github.com/Data-Wise/nexus-cli/issues) page.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

**Download**: [v0.5.0 Release](https://github.com/Data-Wise/nexus-cli/releases/tag/v0.5.0)

**Install**:
```bash
git clone https://github.com/Data-Wise/nexus-cli
cd nexus-cli
git checkout v0.5.0
pip install -e .
```

**Upgrade from v0.4.0**:
```bash
cd nexus-cli
git pull
git checkout v0.5.0
pip install -e . --upgrade
```
