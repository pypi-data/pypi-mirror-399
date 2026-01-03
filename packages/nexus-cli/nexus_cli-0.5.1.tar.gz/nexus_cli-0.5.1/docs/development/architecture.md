# Architecture

Technical architecture and design principles of Nexus CLI.

## Philosophy

> **Nexus does NOT do AI. It provides data and operations. Claude does the thinking.**

Nexus is Claude's "body" for academic work - providing structured access to research data without any AI processing.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE NEXUS ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                      ┌─────────────┐                           │
│                      │   CLAUDE    │  (Brain)                  │
│                      │ • Thinking  │                           │
│                      │ • Planning  │                           │
│                      │ • Writing   │                           │
│                      └──────┬──────┘                           │
│                             │                                   │
│                             │ 4 Integration Patterns            │
│                             │                                   │
│                      ┌──────┴──────┐                           │
│                      │   NEXUS     │  (Body)                   │
│                      │ • Searching │                           │
│                      │ • Reading   │                           │
│                      │ • Writing   │                           │
│                      │ • Organizing│                           │
│                      └──────┬──────┘                           │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              ▼              ▼              ▼                   │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐              │
│       │  ZOTERO  │   │   PDFs   │   │  VAULT   │              │
│       │  2,728   │   │  1,800   │   │ Obsidian │              │
│       │  papers  │   │  files   │   │  notes   │              │
│       └──────────┘   └──────────┘   └──────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Patterns

### 1. MCP Server (Primary)

Claude Desktop/Code calls Nexus tools directly via Model Context Protocol:

```
Claude → MCP Server → Nexus Functions → Data
                  ↓
           Structured Response
```

**Advantages**:
- No API costs
- Direct function calls
- Typed responses
- Stateless operations

**Implementation**: `~/mcp-servers/nexus/`

### 2. CLI Invocation

Claude runs Nexus CLI commands via Bash tool:

```
Claude → Bash → `nexus research zotero search "query"` → JSON
```

**Advantages**:
- Simple integration
- Works in any environment
- Easy debugging

### 3. Piping

Output from Nexus piped to Claude:

```bash
nexus knowledge search "topic" --json | claude -p "Summarize"
```

**Advantages**:
- Unix philosophy
- Composable workflows
- Human-readable

### 4. Skills/Instructions

Claude Code skills teach best practices:

```
Location: plugin/skills/
- knowledge/vault-operations/
- research/zotero-integration/
- teaching/course-management/
- writing/manuscript-management/
```

## Four-Domain Architecture

```
nexus/
├── knowledge/      # 🧠 Obsidian vault, graph viz
├── research/       # 🔬 Zotero, PDFs, literature
├── teaching/       # 📚 Courses, Quarto, materials
├── writing/        # ✍️ Manuscripts, bibliography
└── utils/          # Configuration, helpers
```

### Knowledge Domain

**Purpose**: Manage Obsidian vault and knowledge graph

```python
nexus/knowledge/
├── __init__.py
├── vault.py        # VaultManager - 280 lines (66% cov)
└── search.py       # UnifiedSearch - 100 lines (60% cov)
```

**Key Classes**:
- `VaultManager`: CRUD operations on vault
- `UnifiedSearch`: Cross-source search

**Operations**:
- List/read/search notes
- Find backlinks
- Generate graph data
- Track orphan notes

### Research Domain

**Purpose**: Access research literature (Zotero + PDFs)

```python
nexus/research/
├── __init__.py
├── zotero.py       # ZoteroClient - 193 lines (73% cov)
└── pdf.py          # PDFExtractor - 205 lines (77% cov)
```

**Key Classes**:
- `ZoteroClient`: SQLite interface to Zotero
- `PDFExtractor`: PDF text extraction and search

**Operations**:
- Search Zotero library
- Generate citations (APA, BibTeX)
- Extract PDF text
- Search across PDFs

### Teaching Domain

**Purpose**: Manage courses and teaching materials

```python
nexus/teaching/
├── __init__.py
├── courses.py      # CourseManager - 214 lines (70% cov)
└── quarto.py       # QuartoManager - 162 lines (91% cov)
```

**Key Classes**:
- `CourseManager`: Course and lecture management
- `QuartoManager`: Quarto project operations

**Operations**:
- List courses and lectures
- Get syllabi
- Build Quarto websites
- Validate projects

### Writing Domain

**Purpose**: Track manuscripts and bibliography

```python
nexus/writing/
├── __init__.py
├── manuscript.py   # ManuscriptManager - 239 lines (74% cov)
└── bibliography.py # BibliographyManager - 176 lines (72% cov)
```

**Key Classes**:
- `ManuscriptManager`: Manuscript tracking
- `BibliographyManager`: Bibliography checking

**Operations**:
- List manuscripts
- Track status (draft → review → published)
- Check citations
- Find missing references

## CLI Architecture

Built with [Typer](https://typer.tiangolo.com/) - type-safe CLI framework.

```python
# nexus/cli.py (1029 lines)

from typer import Typer

app = Typer(name="nexus")

# Domain subapps
knowledge_app = Typer(name="knowledge")
research_app = Typer(name="research")
teach_app = Typer(name="teach")
write_app = Typer(name="write")

app.add_typer(knowledge_app)
app.add_typer(research_app)
app.add_typer(teach_app)
app.add_typer(write_app)

# Nested commands
vault_app = Typer(name="vault")
knowledge_app.add_typer(vault_app)

@vault_app.command("search")
def vault_search(query: str, limit: int = 20, json_output: bool = False):
    """Search vault for query."""
    manager = VaultManager(config.vault.path)
    results = manager.search(query, limit=limit)
    
    if json_output:
        console.print_json(results)
    else:
        display_results(results)
```

### Command Hierarchy

```
nexus
├── doctor          # Health check
├── config          # Show config
├── knowledge
│   ├── search      # Unified search
│   └── vault
│       ├── list    # List notes
│       ├── read    # Read note
│       ├── search  # Search vault
│       ├── backlinks
│       ├── graph
│       ├── stats
│       └── orphans
├── research
│   ├── zotero
│   │   ├── search
│   │   ├── get
│   │   ├── cite
│   │   ├── recent
│   │   ├── collections
│   │   └── tags
│   └── pdf
│       ├── list
│       ├── extract
│       └── search
├── teach
│   ├── course
│   │   ├── list
│   │   ├── get
│   │   ├── lectures
│   │   └── syllabus
│   └── quarto
│       ├── build
│       ├── preview
│       └── formats
└── write
    ├── manuscript
    │   ├── list
    │   ├── status
    │   └── update
    └── bib
        ├── check
        ├── find
        └── search
```

## Data Flow

### Example: Search Workflow

```
User/Claude
    │
    ▼
nexus knowledge search "mediation"
    │
    ▼
CLI (cli.py)
    │
    ├──> Config.load()
    │       │
    │       ▼
    │    ~/.config/nexus/config.yaml
    │
    ├──> VaultManager(config.vault.path)
    │       │
    │       ▼
    │    ~/Obsidian/Nexus/
    │       │
    │       ▼
    │    search_index (in-memory)
    │
    └──> ZoteroClient(config.zotero.database)
            │
            ▼
         ~/Zotero/zotero.sqlite
            │
            ▼
         SQL Query
            │
            ▼
         Results
    │
    ▼
JSON or Rich display
```

## Configuration System

### Config File Structure

```yaml
# ~/.config/nexus/config.yaml

vault:
  path: ~/Obsidian/Nexus
  templates: ~/Obsidian/Nexus/_SYSTEM/templates

zotero:
  database: ~/Zotero/zotero.sqlite
  storage: ~/Zotero/storage

pdf:
  directories:
    - ~/Documents/Research/PDFs
    - ~/Zotero/storage

teaching:
  courses_dir: ~/teaching
  quarto_dir: ~/quarto

writing:
  manuscripts_dir: ~/manuscripts
```

### Config Loading

```python
# nexus/utils/config.py

from pydantic_settings import BaseSettings
from pathlib import Path

class VaultConfig(BaseSettings):
    path: Path
    templates: Path | None = None

class ZoteroConfig(BaseSettings):
    database: Path
    storage: Path | None = None

class Config(BaseSettings):
    vault: VaultConfig
    zotero: ZoteroConfig
    pdf: PDFConfig
    teaching: TeachingConfig
    writing: WritingConfig
    
    class Config:
        env_file = Path.home() / ".config/nexus/config.yaml"
    
    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """Load configuration from file."""
        if config_path is None:
            config_path = cls.Config.env_file
        
        with open(config_path) as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
```

## Data Models

### Pydantic Models

All data uses Pydantic for validation:

```python
from pydantic import BaseModel, Field
from pathlib import Path

class SearchResult(BaseModel):
    """Search result from vault."""
    path: str
    title: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    matches: list[str]

class ZoteroItem(BaseModel):
    """Zotero library item."""
    key: str
    title: str
    author: str
    year: int
    type: str
    journal: str | None = None
    doi: str | None = None
    
    def cite_apa(self) -> str:
        """Generate APA citation."""
        ...
```

**Benefits**:
- Type safety
- Automatic validation
- JSON serialization
- IDE autocomplete

## Error Handling

### Exception Hierarchy

```python
class NexusError(Exception):
    """Base exception for Nexus."""
    pass

class ConfigError(NexusError):
    """Configuration errors."""
    pass

class VaultError(NexusError):
    """Vault operation errors."""
    pass

class ZoteroError(NexusError):
    """Zotero operation errors."""
    pass
```

### CLI Error Handling

```python
@vault_app.command("read")
def vault_read(note_name: str):
    """Read a note."""
    try:
        manager = VaultManager(config.vault.path)
        content = manager.read(note_name)
        console.print(content)
    except FileNotFoundError:
        console.print(f"[red]Note not found: {note_name}[/]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(1)
```

## Output Formatting

### Rich Console

All CLI output uses [Rich](https://rich.readthedocs.io/):

```python
from rich.console import Console
from rich.table import Table

console = Console()

# Tables
table = Table(title="Search Results")
table.add_column("Title", style="cyan")
table.add_column("Path", style="dim")
for result in results:
    table.add_row(result.title, result.path)
console.print(table)

# JSON
console.print_json(data)

# Markdown
console.print(Markdown(content))

# Progress bars
with console.status("[bold green]Searching...") as status:
    results = search(query)
```

### JSON Output

Every command supports `--json`:

```python
if json_output:
    console.print_json([r.dict() for r in results])
else:
    display_table(results)
```

## Testing Architecture

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_<module>.py         # Unit tests
├── test_<module>_manager.py # Comprehensive tests
├── test_cli_integration.py  # Integration tests
├── test_validation.py       # Validation tests
└── test_edge_cases.py       # Edge cases
```

### Testing Layers

1. **Unit Tests**: Individual functions
2. **Integration Tests**: Full CLI commands
3. **Validation Tests**: Data model validation
4. **Edge Cases**: Error handling

### Mock Strategy

```python
@patch('subprocess.run')
def test_pdf_extract(mock_run, temp_dir):
    """Test with mocked subprocess."""
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Text content"
    )
    
    extractor = PDFExtractor()
    result = extractor.extract(temp_dir / "test.pdf")
    
    assert "Text content" in result
```

## Performance Considerations

### Caching

```python
from functools import lru_cache

class VaultManager:
    @lru_cache(maxsize=128)
    def search(self, query: str) -> list[SearchResult]:
        """Cached search results."""
        ...
```

### Lazy Loading

```python
class ZoteroClient:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn = None  # Lazy connection
    
    @property
    def conn(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
        return self._conn
```

### Batch Operations

```python
def process_pdfs(pdf_paths: list[Path]) -> list[str]:
    """Process PDFs in parallel."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(extract_text, pdf_paths))
```

## Security

### Input Validation

All user input validated via Pydantic:

```python
class SearchQuery(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    limit: int = Field(ge=1, le=100)
```

### File Path Safety

```python
def safe_read(vault_path: Path, note_path: str) -> str:
    """Safely read note, preventing path traversal."""
    full_path = (vault_path / note_path).resolve()
    
    if not full_path.is_relative_to(vault_path):
        raise ValueError("Invalid note path")
    
    return full_path.read_text()
```

### SQL Injection Prevention

```python
def search_zotero(query: str) -> list[ZoteroItem]:
    """Safe SQL query with parameterization."""
    cursor.execute(
        "SELECT * FROM items WHERE title LIKE ?",
        (f"%{query}%",)
    )
```

## Extension Points

### Custom Commands

Add new commands by extending apps:

```python
# nexus/extensions/custom.py

@research_app.command("custom")
def custom_command(arg: str):
    """Custom research command."""
    ...
```

### Custom Data Sources

Implement the search interface:

```python
class CustomSource:
    def search(self, query: str) -> list[SearchResult]:
        """Implement search."""
        ...
```

### Custom Formats

Add citation formats:

```python
class ZoteroItem:
    def cite_custom(self) -> str:
        """Custom citation format."""
        ...
```

## Deployment

### Installation

```bash
# From source
git clone https://github.com/Data-Wise/nexus-cli
cd nexus-cli
pip install -e .

# From PyPI (future)
pip install nexus-cli
```

### Distribution

```bash
# Build wheel
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Future Architecture

### Planned Enhancements

1. **Plugin System**
   ```python
   nexus/plugins/
   ├── __init__.py
   └── <plugin_name>/
       ├── __init__.py
       └── commands.py
   ```

2. **Web UI**
   ```
   FastAPI server → Vue.js frontend
   ```

3. **Database Backend**
   ```
   SQLite → local cache → faster searches
   ```

4. **Real-time Sync**
   ```
   File watchers → index updates → instant results
   ```

## See Also

- [Testing Guide](testing.md) - Testing practices
- [Contributing Guide](contributing.md) - How to contribute
- [Python API](../reference/api.md) - API documentation
