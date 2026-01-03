## [Unreleased] - 2025-12-25

### Added
- **🎓 Interactive Tutorial System**: Built-in guided learning at three levels
  - `nexus learn` - Browse available tutorials
  - `nexus learn getting-started` - Basic commands and setup (7 steps, ~10 min)
  - `nexus learn medium` - Domain workflows (11 steps, ~20 min)
  - `nexus learn advanced` - Batch operations and integrations (12 steps, ~30 min)
  - Resume capability with `--step N` flag
  - Interactive prompts with hands-on exercises
  - Contextual hints and tips at each step
  - Real-world command examples using actual data
- **Tutorial Documentation**:
  - `TUTORIAL_GUIDE.md` - Comprehensive tutorial system documentation
  - `TUTORIAL_QUICK_REF.md` - Quick reference card for all tutorials
  - Tutorial callouts in Getting Started guides
  - Updated CLI reference with learn commands
- **Comprehensive CI/CD Infrastructure**:
  - Multi-platform testing (Ubuntu, macOS, Windows)
  - Python version matrix (3.11, 3.12, 3.13)
  - Automated code quality checks (ruff, mypy, bandit)
  - Coverage tracking with Codecov
  - Scheduled weekly regression tests
- **Extensive Dogfooding Test Suite**: 56 integration tests (+133%)
  - Research domain: Zotero and PDF operations (8 tests)
  - Teaching domain: Courses and Quarto (4 tests)
  - Writing domain: Manuscripts and Bibliography (11 tests)
  - Knowledge domain: Vault and Search (13 tests)
  - Cross-domain workflows (2 tests)
  - JSON output validation (1 comprehensive test)
  - Edge cases and error handling (6 tests)
- **Environment Variable Configuration**: `NEXUS_CONFIG` for config override
- **JSON Output Fix**: Proper formatting for all JSON commands (33 fixes)

### Changed
- **Test Coverage**: 54.35% → 74.67% (+20.32%)
  - Overall: 69.35% → 74.67% (+5.32%)
  - CLI: 29.85% → 67.36% (+37.51%)
  - Knowledge/Search: 27.00% → 80.00% (+53.00%)
  - Teaching/Quarto: 25.31% → 91.36% (+66.05%)
  - Writing/Bibliography: 20.45% → 74.43% (+53.98%)
  - Research/PDF: 27.32% → 79.51% (+52.19%)
  - Research/Zotero: 23.32% → 72.54% (+49.22%)
  - Writing/Manuscript: 64.51% → 83.38% (+18.87%)
- **Total Tests**: 302 → 422 (+120 tests, +40%)
- **Pydantic V2 Migration**: Updated to ConfigDict (removes deprecation warnings)
- CI workflows now use `uv` for 10-100x faster dependency installation

### Fixed
- NEXUS_CONFIG environment variable not recognized in tests
- JSON output containing invalid control characters (Rich console formatting)
- Pydantic deprecation warnings (migrated to ConfigDict)
- Test environment isolation issues with Typer CliRunner

### Technical
- New GitHub Actions workflows:
  - `.github/workflows/ci.yml`: Enhanced main CI workflow
  - `.github/workflows/test.yml`: Comprehensive platform testing
  - `.github/workflows/quality.yml`: Code quality enforcement
- Test file size: 545 → 1,055 lines (+93%)
- Documentation: +1,500 lines (test summaries, CI/CD guides)
- All tests passing: 422/422 (100%)

# Changelog

All notable changes to Nexus CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-12-25

### Added
- **Graph Export Formats**: Export vault knowledge graphs to multiple formats
  - GraphML format for Gephi, Cytoscape, yEd
  - D3.js format for web visualizations
  - Enhanced JSON format with tag/limit support
  - XML escaping for special characters
- **Batch Manuscript Operations**: Manage multiple manuscripts efficiently
  - `batch-status`: Update status for multiple manuscripts at once
  - `batch-progress`: Update progress for multiple manuscripts
  - `batch-archive`: Archive manuscripts to Archive/ subdirectory
  - `export`: Export metadata to JSON or CSV formats
- **Comprehensive Documentation**: ~9,500 lines of new documentation
  - Tutorial: First Steps guide
  - Tutorial: Vault Setup guide
  - Tutorial: Zotero Integration guide
  - Tutorial: Graph Visualization guide
  - Reference: Complete Python API documentation
  - Reference: MCP Server documentation (17 tools)
  - Development: Testing guide (302 tests)
  - Development: Architecture documentation
- **New Test Coverage**: 27 new tests (+9.8%)
  - `test_graph_export.py`: 11 tests for graph export formats
  - `test_manuscript_batch.py`: 16 tests for batch operations

### Changed
- Test coverage: 49.88% → 54.35% (+4.47%)
- Manuscript module coverage: 50.99% → 78.03% (+27.04%)
- Total tests: 275 → 302 (+27 tests)
- VaultManager: +39 lines (export methods)
- ManuscriptManager: +116 lines (batch operations)

### Technical
- New methods in `VaultManager`: `export_graphml()`, `export_d3()`, `_escape_xml()`
- New methods in `ManuscriptManager`: `batch_update_status()`, `batch_update_progress()`, `batch_archive()`, `batch_export_metadata()`
- Consistent batch operation return format: `{success: [], failed: [], errors: {}}`
- Atomic batch operations for data integrity

## [0.4.0] - 2025-12-25

### Added
- Enhanced CI/CD Pipeline
  - Matrix testing: 2 OS × 3 Python versions
  - Security scanning with Bandit
  - Coverage enforcement (40% minimum)
  - Type checking with mypy
  - Automated artifact uploads
- Comprehensive Documentation Site
  - MkDocs with Material theme
  - Installation, Quick Start, Configuration guides
  - Domain-specific user guides
  - Auto-deployment to GitHub Pages
- Test Suite Expansion: 58 new tests
  - `test_pdf_extractor.py`: PDFExtractor comprehensive tests (23 tests)
  - `test_quarto_manager.py`: QuartoManager comprehensive tests (29 tests)
  - `test_zotero_client.py`: ZoteroClient comprehensive tests (28 tests)
- Build Configuration Updates
  - Added dev tools: pytest-mock, bandit, coverage-badge
  - Added docs tools: mkdocstrings, git-revision-date
  - Test markers and coverage config

### Changed
- Test coverage: 43% → 53% (+10%)
- Total tests: 177 → 235 (+58 tests)
- Major coverage improvements:
  - PDF module: +46%
  - Search module: +32%
  - Vault module: +9%

## [0.3.0] - 2025-12-25

### Added
- Comprehensive test suite with 235+ tests (53% coverage)
- Enhanced GitHub Actions CI/CD with matrix testing, security scanning
- Coverage threshold enforcement (40%+)
- MCP server with 17 tools for Claude Desktop integration
- Vault graph visualization with `nexus knowledge vault graph`
- Graph statistics with connectivity analysis
- Improved PDF text extraction with smart cleaning
- Better context extraction for PDF search results
- Validation tests for all data models
- Edge case and error handling tests
- CLI integration tests
- Advanced test coverage for research modules

### Changed
- Enhanced CI workflow with poppler installation
- Improved PDF text cleaning (ligatures, soft hyphens, artifacts)
- Better title extraction from PDFs
- Ranked search results for PDF queries
- Updated pyproject.toml to v0.3.0
- Enhanced .gitignore for test artifacts

### Fixed
- Multiple test fixes and improvements
- Better error handling in edge cases
- Improved validation of user inputs

## [0.2.0] - 2025-12-24

### Added
- MCP server at `~/mcp-servers/nexus/`
- 17 MCP tools covering all domains
- Enhanced PDF extraction with `-raw` flag
- Smart PDF text cleaning and title extraction
- Vault graph generation (`graph()` method)
- Graph statistics calculation
- New test modules (test_zotero.py, test_pdf.py, test_quarto.py, test_search.py)

### Changed
- Improved PDF search with better context windows
- Better ranking for search results
- Test coverage increased from 36% to 38%

## [0.1.0] - 2025-12-24

### Added
- Core CLI infrastructure with Typer
- Four main domains: Knowledge, Research, Teaching, Writing
- Knowledge domain:
  - Vault search, read, write operations
  - Recent notes, backlinks, orphans
  - Daily note creation
  - Template support
- Research domain:
  - Zotero library search and citation
  - PDF extraction and search
  - Literature management
- Teaching domain:
  - Course management
  - Quarto integration
  - Syllabus and lecture tracking
- Writing domain:
  - Manuscript tracking
  - Bibliography checking
  - Citation validation
- Unified search across all knowledge sources
- JSON output for all commands
- Claude Code plugin integration
- Configuration management system
- Health check (`nexus doctor`)
- Installation script
- Comprehensive README and documentation
- GitHub Actions CI workflow
- 58 initial tests with 36% coverage

### Technical
- Python 3.11+ support
- Typer for CLI
- Rich for terminal output
- Pydantic for configuration
- PyYAML for parsing
- pytest for testing

## [Unreleased]

### Planned for v0.6.0
- Additional graph export formats (GML, Cytoscape JSON)
- Batch operations for other domains (courses, bibliography)
- Interactive CLI mode with prompts
- Performance benchmarks with pytest-benchmark
- Further test coverage improvements (target: 60%+)
- Plugin system for custom exporters
- Export to graph databases (Neo4j, ArangoDB)

---

[0.5.0]: https://github.com/Data-Wise/nexus-cli/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Data-Wise/nexus-cli/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Data-Wise/nexus-cli/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Data-Wise/nexus-cli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Data-Wise/nexus-cli/releases/tag/v0.1.0
