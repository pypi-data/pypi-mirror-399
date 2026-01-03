# Changelog

All notable changes to Nexus CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Planned
- Further test coverage improvements (target: 60%+)
- Additional MCP tools
- More graph visualization options
- Enhanced PDF extraction
- Additional citation styles
- Web interface (possible future enhancement)

---

[0.3.0]: https://github.com/Data-Wise/nexus-cli/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Data-Wise/nexus-cli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Data-Wise/nexus-cli/releases/tag/v0.1.0
