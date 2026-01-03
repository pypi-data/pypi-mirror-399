# Testing Guide

Comprehensive guide to testing Nexus CLI.

## Test Suite Overview

Nexus has **275 tests** with **53% coverage** across 16 test modules.

### Test Categories

1. **Unit Tests** - Individual functions and classes
2. **Integration Tests** - CLI commands end-to-end
3. **Validation Tests** - Data model validation
4. **Edge Case Tests** - Error handling and boundaries

## Running Tests

### Basic Usage

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run specific file
pytest tests/test_vault.py

# Run specific test
pytest tests/test_vault.py::TestVaultManager::test_search

# Run tests matching pattern
pytest -k "search"
```

### With Coverage

```bash
# Generate coverage report
pytest --cov=nexus

# HTML report
pytest --cov=nexus --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=nexus --cov-report=term-missing

# XML report (for CI)
pytest --cov=nexus --cov-report=xml
```

### Test Markers

```bash
# Run only integration tests
pytest -m integration

# Skip integration tests
pytest -m "not integration"

# Run slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Test Structure

### Test Organization

```
tests/
├── conftest.py                 # Shared fixtures
├── test_bibliography.py        # Bibliography tests (13)
├── test_cli.py                 # CLI basic tests (13)
├── test_cli_commands.py        # CLI command tests (19)
├── test_cli_integration.py     # Integration tests (19)
├── test_config.py              # Config tests (3)
├── test_courses.py             # Course tests (9)
├── test_edge_cases.py          # Edge case tests (25)
├── test_manuscript.py          # Manuscript tests (11)
├── test_pdf.py                 # PDF basic tests (3)
├── test_pdf_extractor.py       # PDF extractor tests (23) ⭐
├── test_quarto.py              # Quarto basic tests (4)
├── test_quarto_manager.py      # Quarto manager tests (29) ⭐
├── test_search.py              # Search tests (21)
├── test_validation.py          # Validation tests (28)
├── test_vault.py               # Vault tests (22)
├── test_zotero.py              # Zotero basic tests (5)
└── test_zotero_client.py       # Zotero client tests (28) ⭐
```

⭐ = Comprehensive test modules added in v0.4.0

### Fixtures (`conftest.py`)

Common fixtures available to all tests:

```python
import pytest
from pathlib import Path

@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for tests."""
    return tmp_path

@pytest.fixture
def sample_vault(temp_dir):
    """Create a sample vault structure."""
    vault = temp_dir / "vault"
    vault.mkdir()
    
    # Create sample notes
    (vault / "note1.md").write_text("# Note 1\nContent with [[note2]]")
    (vault / "note2.md").write_text("# Note 2\nContent")
    
    return vault

@pytest.fixture
def mock_zotero_db(temp_dir):
    """Create a mock Zotero database."""
    db_path = temp_dir / "zotero.sqlite"
    # Create SQLite database with test data
    ...
    return db_path
```

## Writing Tests

### Unit Test Example

```python
# tests/test_vault.py
import pytest
from nexus.knowledge.vault import VaultManager

class TestVaultManager:
    """Tests for VaultManager class."""
    
    def test_list_notes(self, sample_vault):
        """Test listing notes in vault."""
        manager = VaultManager(sample_vault)
        notes = manager.list_notes()
        
        assert len(notes) == 2
        assert "note1.md" in notes
        assert "note2.md" in notes
    
    def test_search(self, sample_vault):
        """Test searching vault content."""
        manager = VaultManager(sample_vault)
        results = manager.search("content")
        
        assert len(results) == 2
        assert all(r.score > 0 for r in results)
    
    def test_read_nonexistent_note(self, sample_vault):
        """Test reading a note that doesn't exist."""
        manager = VaultManager(sample_vault)
        
        with pytest.raises(FileNotFoundError):
            manager.read("nonexistent.md")
```

### Integration Test Example

```python
# tests/test_cli_integration.py
import subprocess
import json

class TestCLIIntegration:
    """Test CLI commands end-to-end."""
    
    def test_vault_search_json(self):
        """Test vault search with JSON output."""
        result = subprocess.run(
            ["nexus", "knowledge", "search", "test", "--json"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "results" in data
        assert isinstance(data["results"], list)
```

### Mocking External Dependencies

```python
# tests/test_pdf_extractor.py
import pytest
from unittest.mock import patch, MagicMock
from nexus.research.pdf import PDFExtractor

class TestPDFExtractor:
    """Tests for PDFExtractor class."""
    
    @patch('subprocess.run')
    def test_extract_with_mock(self, mock_run, temp_dir):
        """Test PDF extraction with mocked subprocess."""
        # Mock pdftotext output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Extracted text content"
        )
        
        extractor = PDFExtractor()
        text = extractor.extract(temp_dir / "test.pdf")
        
        assert "Extracted text content" in text
        mock_run.assert_called_once()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("query,expected_count", [
    ("mediation", 5),
    ("causal", 3),
    ("nonexistent", 0),
])
def test_search_queries(sample_vault, query, expected_count):
    """Test various search queries."""
    manager = VaultManager(sample_vault)
    results = manager.search(query)
    assert len(results) == expected_count
```

### Testing Error Cases

```python
def test_invalid_config_path():
    """Test handling of invalid config path."""
    from nexus.utils.config import Config, ConfigError
    
    with pytest.raises(ConfigError):
        Config.load(Path("/nonexistent/config.yaml"))

def test_empty_vault(temp_dir):
    """Test vault with no markdown files."""
    manager = VaultManager(temp_dir)
    notes = manager.list_notes()
    assert len(notes) == 0
```

## Coverage Goals

### Current Coverage (v0.4.0)

| Module | Coverage | Status |
|--------|----------|--------|
| `teaching/quarto.py` | 91% | ✅ Excellent |
| `utils/config.py` | 80% | ✅ Good |
| `research/pdf.py` | 77% | ✅ Good |
| `writing/manuscript.py` | 74% | ✅ Good |
| `research/zotero.py` | 73% | ✅ Good |
| `writing/bibliography.py` | 72% | ✅ Good |
| `teaching/courses.py` | 70% | ✅ Good |
| `knowledge/vault.py` | 66% | ⚠️ Moderate |
| `knowledge/search.py` | 60% | ⚠️ Moderate |
| `cli.py` | 21% | ❌ Needs Work |

### Coverage Targets

- **Minimum**: 40% (enforced in CI)
- **Good**: 60%+
- **Excellent**: 80%+
- **Goal for v0.5.0**: 60% overall

## Testing Best Practices

### 1. Test One Thing

```python
# ❌ Bad: Tests multiple things
def test_vault_operations(sample_vault):
    manager = VaultManager(sample_vault)
    notes = manager.list_notes()
    assert len(notes) > 0
    results = manager.search("test")
    assert len(results) > 0

# ✅ Good: Focused tests
def test_list_notes(sample_vault):
    manager = VaultManager(sample_vault)
    notes = manager.list_notes()
    assert len(notes) == 2

def test_search(sample_vault):
    manager = VaultManager(sample_vault)
    results = manager.search("test")
    assert len(results) == 1
```

### 2. Use Descriptive Names

```python
# ❌ Bad
def test_1():
    ...

# ✅ Good
def test_vault_search_returns_matching_notes():
    ...
```

### 3. Arrange-Act-Assert

```python
def test_vault_search():
    # Arrange
    vault = VaultManager("/path/to/vault")
    query = "mediation"
    
    # Act
    results = vault.search(query)
    
    # Assert
    assert len(results) > 0
    assert all(query.lower() in r.content.lower() for r in results)
```

### 4. Use Fixtures for Setup

```python
@pytest.fixture
def vault_with_data(temp_dir):
    """Create vault with test data."""
    vault = temp_dir / "vault"
    vault.mkdir()
    
    for i in range(10):
        (vault / f"note{i}.md").write_text(f"# Note {i}\nContent {i}")
    
    return vault

def test_with_fixture(vault_with_data):
    manager = VaultManager(vault_with_data)
    assert len(manager.list_notes()) == 10
```

### 5. Test Edge Cases

```python
def test_search_empty_query(sample_vault):
    """Test search with empty string."""
    manager = VaultManager(sample_vault)
    results = manager.search("")
    assert len(results) == 0

def test_search_special_characters(sample_vault):
    """Test search with regex special chars."""
    manager = VaultManager(sample_vault)
    results = manager.search("note[1-2]")  # Should not crash
    assert isinstance(results, list)
```

## Continuous Integration

### GitHub Actions

Tests run automatically on every push:

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.11', '3.12', '3.13']
    
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest --cov=nexus --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Coverage Enforcement

Build fails if coverage drops below 40%:

```yaml
- name: Check coverage threshold
  run: |
    coverage report --fail-under=40
```

## Debugging Tests

### Run Single Test with Output

```bash
pytest tests/test_vault.py::TestVaultManager::test_search -vv -s
```

### Use pdb Debugger

```python
def test_with_debugger(sample_vault):
    manager = VaultManager(sample_vault)
    
    import pdb; pdb.set_trace()  # Breakpoint
    
    results = manager.search("test")
    assert len(results) > 0
```

### Print Debug Info

```bash
pytest --capture=no  # Show print() output
pytest -s           # Short version
```

### Failed Test Output

```bash
pytest --tb=short   # Short traceback
pytest --tb=long    # Detailed traceback
pytest --tb=no      # No traceback
```

## Performance Testing

### Benchmark Tests

```python
import pytest

@pytest.mark.benchmark
def test_search_performance(benchmark, sample_vault):
    """Benchmark vault search performance."""
    manager = VaultManager(sample_vault)
    result = benchmark(manager.search, "test")
    assert len(result) > 0
```

Run benchmarks:
```bash
pytest --benchmark-only
```

### Profile Tests

```bash
pytest --profile
```

## Test Data

### Creating Test Fixtures

```python
@pytest.fixture
def zotero_test_data():
    """Sample Zotero items for testing."""
    return [
        {
            "key": "baron1986",
            "title": "The moderator-mediator variable distinction",
            "author": "Baron, R. M.; Kenny, D. A.",
            "year": 1986
        },
        {
            "key": "mackinnon2007",
            "title": "Introduction to Statistical Mediation Analysis",
            "author": "MacKinnon, David P.",
            "year": 2007
        }
    ]
```

### Snapshot Testing

For complex outputs:

```python
def test_graph_output_snapshot(sample_vault, snapshot):
    """Test graph output matches snapshot."""
    manager = VaultManager(sample_vault)
    graph = manager.generate_graph()
    assert graph == snapshot
```

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD)
2. **Achieve 60%+ coverage** for new code
3. **Add integration tests** for CLI commands
4. **Test error cases** 
5. **Update this guide** if adding new patterns

## See Also

- [Contributing Guide](contributing.md) - Contribution guidelines
- [Architecture](architecture.md) - System architecture
- [CLI Reference](../reference/cli.md) - Command reference

## Coverage by Module

Current coverage statistics:

| Module | Coverage | Status |
|--------|----------|--------|
| teaching/quarto.py | 91.36% | ✅ Excellent |
| writing/manuscript.py | 83.38% | ✅ Great |
| utils/config.py | 82.56% | ✅ Great |
| knowledge/search.py | 80.00% | ✅ Great |
| research/pdf.py | 79.51% | ✅ Great |
| knowledge/vault.py | 78.06% | ✅ Good |
| writing/bibliography.py | 74.43% | ✅ Good |
| research/zotero.py | 72.54% | ✅ Good |
| teaching/courses.py | 70.56% | ✅ Good |
| cli.py | 67.36% | ✅ Good |

## Dogfooding Test Suite

The project includes 56 comprehensive dogfooding tests that test real workflows end-to-end:

### Research Domain (8 tests)
- Zotero operations: search, tags, collections, recent
- PDF operations: list, search, JSON output
- Coverage: Zotero 72.54%, PDF 79.51%

### Teaching Domain (4 tests)
- Course management: list courses, JSON output
- Quarto operations: info, formats
- Coverage: Courses 70.56%, Quarto 91.36%

### Writing Domain (11 tests)
- Manuscript operations: list, show, stats, deadlines
- Batch operations: status, progress, archive, export
- Bibliography: list, search, check, zotero integration
- Coverage: Manuscript 83.38%, Bibliography 74.43%

### Knowledge Domain (13 tests)
- Vault operations: search, read, write, recent, backlinks, orphans
- Graph operations: basic, tags, limits
- Export operations: GraphML, D3, JSON
- Advanced features: templates, daily notes
- Coverage: Vault 78.06%, Search 80.00%

### Integration & Edge Cases (6 tests)
- Cross-domain workflows
- Error handling
- JSON output validation

## CI/CD Testing

Automated testing runs on every push:

- **Platforms**: Ubuntu, macOS, Windows
- **Python Versions**: 3.11, 3.12, 3.13
- **Total Configurations**: 9 (3 OS × 3 Python versions)
- **Quality Checks**: ruff (linting), mypy (type checking), bandit (security)
- **Scheduled**: Weekly regression tests every Monday

See [GitHub Actions](https://github.com/Data-Wise/nexus-cli/actions) for live status.
