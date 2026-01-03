# Python API Reference

Nexus CLI can be used as a Python library for programmatic access to your research workflow.

## Installation

```bash
pip install -e .
# or
pip install nexus-cli
```

## Quick Start

```python
from nexus.knowledge.vault import VaultManager
from nexus.research.zotero import ZoteroClient
from nexus.utils.config import Config

# Load configuration
config = Config.load()

# Initialize managers
vault = VaultManager(config.vault.path)
zotero = ZoteroClient(config.zotero.database)

# Search vault
results = vault.search("mediation")
for note in results:
    print(f"- {note.title}")

# Search Zotero
papers = zotero.search("causal inference", limit=5)
for paper in papers:
    print(f"{paper.title} ({paper.year})")
```

## Core Modules

### Configuration

#### `nexus.utils.config.Config`

Configuration management.

```python
from nexus.utils.config import Config

# Load from default location (~/.config/nexus/config.yaml)
config = Config.load()

# Load from custom path
config = Config.load(Path("/custom/config.yaml"))

# Access config values
print(config.vault.path)
print(config.zotero.database)
```

**Attributes:**

- `vault: VaultConfig` - Vault configuration
- `zotero: ZoteroConfig` - Zotero configuration  
- `pdf: PDFConfig` - PDF configuration

**Methods:**

- `load(config_path: Path | None = None) -> Config` - Load configuration
- `get_vault_path() -> Path` - Get vault path with expansion
- `get_zotero_db() -> Path` - Get Zotero database path

### Knowledge Domain

#### `nexus.knowledge.vault.VaultManager`

Manage Obsidian vault operations.

```python
from nexus.knowledge.vault import VaultManager

vault = VaultManager("/path/to/vault")

# List all notes
notes = vault.list_notes()

# Read a note
content = vault.read("Note Title")

# Search
results = vault.search("query", limit=10)

# Get backlinks
backlinks = vault.get_backlinks("Target Note")

# Generate graph
graph = vault.generate_graph(include_tags=True)
```

**Methods:**

**`__init__(vault_path: Path)`**
Initialize vault manager.

**`list_notes(include_templates: bool = False) -> list[str]`**
List all markdown files in vault.

- `include_templates` - Include template files (default: False)
- Returns: List of note paths relative to vault root

**`read(note_name: str) -> str`**
Read note content.

- `note_name` - Note title or path
- Returns: Note content as string
- Raises: `FileNotFoundError` if note doesn't exist

**`search(query: str, limit: int = 20, case_sensitive: bool = False) -> list[SearchResult]`**
Search vault content.

- `query` - Search term or regex pattern
- `limit` - Maximum results
- `case_sensitive` - Case-sensitive search
- Returns: List of `SearchResult` objects

**`get_backlinks(note_name: str) -> dict[str, list[str]]`**
Find notes linking to a specific note.

- `note_name` - Target note title
- Returns: Dict mapping note paths to lists of link contexts

**`generate_graph(include_tags: bool = False, limit: int | None = None) -> dict`**
Generate graph visualization data.

- `include_tags` - Include tag nodes
- `limit` - Limit to N most connected nodes
- Returns: Dict with `nodes` and `edges` lists

**`get_stats() -> dict`**
Get vault statistics.

- Returns: Dict with counts and metrics

#### `nexus.knowledge.search.UnifiedSearch`

Search across multiple sources.

```python
from nexus.knowledge.search import UnifiedSearch

searcher = UnifiedSearch(config)

# Search all sources
results = searcher.search("mediation", sources=["vault", "zotero", "pdf"])

# Search specific source
vault_results = searcher.search("topic", sources=["vault"])
```

**Methods:**

**`search(query: str, sources: list[str] | None = None, limit: int = 20) -> dict`**
Unified search across sources.

- `query` - Search query
- `sources` - List of sources: `["vault", "zotero", "pdf"]`
- `limit` - Results per source
- Returns: Dict with results grouped by source

### Research Domain

#### `nexus.research.zotero.ZoteroClient`

Interface to Zotero library.

```python
from nexus.research.zotero import ZoteroClient

zotero = ZoteroClient("/path/to/zotero.sqlite")

# Search
papers = zotero.search("mediation", limit=10)

# Get specific item
item = zotero.get_item("baron1986")

# Generate citation
citation = zotero.cite("baron1986", format="apa")

# Get recent items
recent = zotero.get_recent(limit=20)
```

**Methods:**

**`search(query: str, limit: int = 20, field: str | None = None) -> list[ZoteroItem]`**
Search Zotero library.

- `query` - Search term
- `limit` - Maximum results
- `field` - Specific field to search (title, author, year)
- Returns: List of `ZoteroItem` objects

**`get_item(key: str) -> ZoteroItem | None`**
Get item by citation key.

- `key` - Zotero item key
- Returns: `ZoteroItem` or None

**`cite(key: str, format: str = "apa") -> str`**
Generate citation.

- `key` - Item key
- `format` - Citation format ("apa" or "bibtex")
- Returns: Formatted citation string

**`get_recent(limit: int = 10) -> list[ZoteroItem]`**
Get recently added items.

- `limit` - Number of items
- Returns: List of `ZoteroItem` objects

#### `nexus.research.pdf.PDFExtractor`

Extract and search PDF documents.

```python
from nexus.research.pdf import PDFExtractor

pdf = PDFExtractor(directories=["/path/to/pdfs"])

# List PDFs
pdfs = pdf.list_pdfs()

# Extract text
text = pdf.extract("/path/to/paper.pdf", pages=(1, 5))

# Search across PDFs
results = pdf.search("bootstrap", limit=10)
```

**Methods:**

**`list_pdfs(directories: list[Path] | None = None) -> list[Path]`**
List all PDF files.

- `directories` - Directories to search (uses configured if None)
- Returns: List of PDF file paths

**`extract(pdf_path: Path, pages: tuple[int, int] | None = None) -> str`**
Extract text from PDF.

- `pdf_path` - Path to PDF file
- `pages` - Optional page range (start, end)
- Returns: Extracted text

**`search(query: str, directories: list[Path] | None = None, limit: int = 10) -> list[PDFSearchResult]`**
Search PDF content.

- `query` - Search term or regex
- `directories` - Directories to search
- `limit` - Maximum results
- Returns: List of `PDFSearchResult` objects

### Writing Domain

#### `nexus.writing.manuscript.ManuscriptManager`

Track manuscript status and metadata.

```python
from nexus.writing.manuscript import ManuscriptManager

manager = ManuscriptManager("/path/to/manuscripts")

# List manuscripts
manuscripts = manager.list_manuscripts()

# Get status
status = manager.get_status("my-paper")

# Update status
manager.update_status("my-paper", status="under_review", target="PNAS")
```

#### `nexus.writing.bibliography.BibliographyManager`

Manage bibliography files.

```python
from nexus.writing.bibliography import BibliographyManager

bib_manager = BibliographyManager("/path/to/manuscripts")

# Find .bib files
bib_files = bib_manager.find_bib_files()

# Parse bibliography
entries = bib_manager.parse_bibliography("refs.bib")

# Check citations
missing = bib_manager.check_citations("manuscript.tex", "refs.bib")
```

### Teaching Domain

#### `nexus.teaching.courses.CourseManager`

Manage course materials.

```python
from nexus.teaching.courses import CourseManager

courses = CourseManager("/path/to/teaching")

# List courses
course_list = courses.list_courses()

# Get course details
course = courses.get_course("STAT440")

# List lectures
lectures = courses.list_lectures("STAT440")
```

#### `nexus.teaching.quarto.QuartoManager`

Manage Quarto projects.

```python
from nexus.teaching.quarto import QuartoManager

quarto = QuartoManager("/path/to/quarto-project")

# Detect project type
is_quarto = quarto.is_quarto_project()

# Get project formats
formats = quarto.get_formats()

# Validate project
is_valid = quarto.validate_project()
```

## Data Models

### `SearchResult`

```python
@dataclass
class SearchResult:
    path: str
    title: str
    content: str
    score: float
    matches: list[str]
```

### `ZoteroItem`

```python
@dataclass
class ZoteroItem:
    key: str
    title: str
    author: str
    year: int
    type: str
    journal: str | None
    doi: str | None
    abstract: str | None
    
    def to_dict(self) -> dict:
        ...
    
    def cite_apa(self) -> str:
        ...
    
    def cite_bibtex(self) -> str:
        ...
```

### `PDFSearchResult`

```python
@dataclass
class PDFSearchResult:
    path: Path
    title: str
    score: float
    context: str
    page: int | None
```

### `Manuscript`

```python
@dataclass
class Manuscript:
    path: Path
    title: str
    status: str  # draft, review, revision, published
    target: str | None
    progress: int  # 0-100
    
    def status_emoji(self) -> str:
        ...
```

## Error Handling

```python
from nexus.utils.config import ConfigError
from pathlib import Path

try:
    vault = VaultManager(Path("/nonexistent"))
except FileNotFoundError:
    print("Vault not found")

try:
    config = Config.load(Path("/bad/config.yaml"))
except ConfigError as e:
    print(f"Config error: {e}")
```

## Examples

### Example 1: Literature Review Pipeline

```python
from nexus.research.zotero import ZoteroClient
from nexus.knowledge.vault import VaultManager
from nexus.utils.config import Config

config = Config.load()
zotero = ZoteroClient(config.zotero.database)
vault = VaultManager(config.vault.path)

# Search for papers
papers = zotero.search("mediation analysis", limit=20)

# Create literature notes
for paper in papers:
    note_path = vault.vault_path / "Literature" / f"{paper.key}.md"
    
    content = f"""---
title: {paper.title}
author: {paper.author}
year: {paper.year}
zotero_key: {paper.key}
tags: [literature]
---

# {paper.title}

**Citation**: @{paper.key}

## Abstract
{paper.abstract or 'No abstract available'}

## Summary

## Key Points

## Connections
"""
    
    note_path.write_text(content)
    print(f"Created: {paper.key}.md")
```

### Example 2: Citation Extraction

```python
from nexus.research.zotero import ZoteroClient
from nexus.writing.manuscript import ManuscriptManager
import re

zotero = ZoteroClient("/path/to/zotero.sqlite")
manuscripts = ManuscriptManager("/path/to/manuscripts")

# Read manuscript
manuscript_text = Path("paper.tex").read_text()

# Find citation keys
cite_pattern = r"\\cite(?:p|t|author)?\{([^}]+)\}"
keys = re.findall(cite_pattern, manuscript_text)
keys = [k.strip() for cite in keys for k in cite.split(',')]

# Generate bibliography
print("% Bibliography\n")
for key in set(keys):
    citation = zotero.cite(key, format="bibtex")
    if citation:
        print(citation)
        print()
```

### Example 3: Graph Analysis

```python
from nexus.knowledge.vault import VaultManager
import networkx as nx

vault = VaultManager("/path/to/vault")
graph_data = vault.generate_graph(include_tags=False)

# Build NetworkX graph
G = nx.Graph()
for node in graph_data['nodes']:
    G.add_node(node['id'], **node)
for edge in graph_data['edges']:
    G.add_edge(edge['source'], edge['target'])

# Find central concepts
pagerank = nx.pagerank(G)
top_concepts = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

print("Top 10 Central Concepts:")
for concept, score in top_concepts:
    print(f"  {concept}: {score:.4f}")
```

## Type Hints

Nexus uses full type hints. Enable type checking:

```bash
mypy your_script.py
```

## Testing

```python
import pytest
from nexus.knowledge.vault import VaultManager

def test_vault_search(tmp_path):
    # Create test vault
    (tmp_path / "test.md").write_text("# Test Note\nContent here")
    
    vault = VaultManager(tmp_path)
    results = vault.search("content")
    
    assert len(results) == 1
    assert results[0].title == "Test Note"
```

## See Also

- [CLI Reference](cli.md) - Command-line interface
- [MCP Server](mcp.md) - Model Context Protocol integration
- [User Guides](../guide/overview.md) - Domain-specific guides
