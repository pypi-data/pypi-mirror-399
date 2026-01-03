# MCP Server Reference

The Nexus MCP (Model Context Protocol) Server provides Claude Desktop and Claude Code CLI with direct access to your research workflow through tool calling.

## What is MCP?

MCP (Model Context Protocol) is Anthropic's standard for connecting Claude to external tools and data sources. The Nexus MCP Server exposes 17 tools that Claude can call directly.

**Key Benefits**:
- ✅ No API costs - works with Claude Desktop/Code
- ✅ Direct access - Claude calls Nexus functions directly
- ✅ Structured output - Tools return typed data
- ✅ Stateless - Each call is independent

## Installation

The MCP server is located at `~/mcp-servers/nexus/`.

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_nexus"
      ],
      "env": {
        "NEXUS_CONFIG": "/Users/username/.config/nexus/config.yaml"
      }
    }
  }
}
```

### For Claude Code CLI

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "nexus": {
      "command": "python",
      "args": ["-m", "mcp_server_nexus"],
      "env": {
        "NEXUS_CONFIG": "/Users/username/.config/nexus/config.yaml"
      }
    }
  }
}
```

Restart Claude Desktop/Code after configuration.

## Available Tools

### Knowledge Domain (5 tools)

#### `vault_search`
Search notes in Obsidian vault.

**Parameters**:
- `query` (string, required) - Search term
- `limit` (integer, optional) - Max results (default: 20)
- `case_sensitive` (boolean, optional) - Case-sensitive search

**Returns**:
```json
{
  "results": [
    {
      "path": "Concepts/Mediation.md",
      "title": "Mediation Analysis",
      "content": "...",
      "score": 0.95,
      "matches": ["mediation", "mediator"]
    }
  ],
  "count": 1
}
```

**Example**:
> "Search my vault for notes about mediation analysis"

#### `vault_read`
Read a specific note.

**Parameters**:
- `note_name` (string, required) - Note title or path

**Returns**:
```json
{
  "title": "Mediation Analysis",
  "path": "Concepts/Mediation.md",
  "content": "# Mediation Analysis\n\nContent...",
  "word_count": 543,
  "links": ["Causal Inference", "Regression Analysis"]
}
```

**Example**:
> "Read my note on causal inference"

#### `vault_list`
List all notes in vault.

**Parameters**:
- `include_templates` (boolean, optional) - Include template files

**Returns**:
```json
{
  "notes": [
    "Concepts/Mediation.md",
    "Literature/Baron 1986.md",
    ...
  ],
  "count": 342
}
```

**Example**:
> "List all notes in my vault"

#### `vault_backlinks`
Find notes linking to a specific note.

**Parameters**:
- `note_name` (string, required) - Target note title

**Returns**:
```json
{
  "note": "Mediation Analysis",
  "backlinks": {
    "Projects/Current Research.md": [
      "See [[Mediation Analysis]] for details",
      "Apply [[Mediation Analysis]] framework"
    ],
    "Literature/MacKinnon 2007.md": [
      "Introduces [[Mediation Analysis]]"
    ]
  },
  "count": 2
}
```

**Example**:
> "What notes link to my mediation analysis note?"

#### `vault_graph`
Generate vault graph visualization data.

**Parameters**:
- `include_tags` (boolean, optional) - Include tag nodes
- `limit` (integer, optional) - Limit to N most connected nodes

**Returns**:
```json
{
  "nodes": [
    {
      "id": "Mediation Analysis",
      "label": "Mediation Analysis",
      "type": "note",
      "connections": 45,
      "path": "Concepts/Mediation.md"
    }
  ],
  "edges": [
    {
      "source": "Mediation Analysis",
      "target": "Causal Inference",
      "weight": 3
    }
  ],
  "stats": {
    "node_count": 342,
    "edge_count": 1247
  }
}
```

**Example**:
> "Generate a graph of my knowledge base"

### Research Domain (7 tools)

#### `zotero_search`
Search Zotero library.

**Parameters**:
- `query` (string, required) - Search term
- `limit` (integer, optional) - Max results (default: 10)
- `field` (string, optional) - Specific field (title, author, year)

**Returns**:
```json
{
  "results": [
    {
      "key": "baron1986",
      "title": "The moderator-mediator variable distinction...",
      "author": "Baron, R. M.; Kenny, D. A.",
      "year": 1986,
      "type": "journalArticle",
      "journal": "Journal of Personality and Social Psychology"
    }
  ],
  "count": 1
}
```

**Example**:
> "Find papers by Baron and Kenny in my Zotero library"

#### `zotero_get`
Get specific Zotero item by key.

**Parameters**:
- `key` (string, required) - Zotero item key

**Returns**:
```json
{
  "key": "baron1986",
  "title": "The moderator-mediator variable distinction...",
  "author": "Baron, R. M.; Kenny, D. A.",
  "year": 1986,
  "type": "journalArticle",
  "journal": "Journal of Personality and Social Psychology",
  "volume": "51",
  "issue": "6",
  "pages": "1173-1182",
  "doi": "10.1037/0022-3514.51.6.1173",
  "abstract": "..."
}
```

**Example**:
> "Get details for zotero item baron1986"

#### `zotero_cite`
Generate citation for a paper.

**Parameters**:
- `key` (string, required) - Item key
- `format` (string, optional) - Citation format (apa, bibtex)

**Returns**:
```json
{
  "key": "baron1986",
  "format": "apa",
  "citation": "Baron, R. M., & Kenny, D. A. (1986). The moderator-mediator variable distinction in social psychological research: Conceptual, strategic, and statistical considerations. Journal of Personality and Social Psychology, 51(6), 1173-1182."
}
```

**Example**:
> "Give me the APA citation for baron1986"

#### `zotero_recent`
Get recently added items.

**Parameters**:
- `limit` (integer, optional) - Number of items (default: 10)

**Returns**:
```json
{
  "items": [...],
  "count": 10
}
```

**Example**:
> "What are the 5 most recent papers I added to Zotero?"

#### `pdf_list`
List all PDF files.

**Parameters**:
- `directories` (array, optional) - Directories to search

**Returns**:
```json
{
  "pdfs": [
    "/path/to/paper1.pdf",
    "/path/to/paper2.pdf"
  ],
  "count": 1847
}
```

**Example**:
> "How many PDFs do I have?"

#### `pdf_extract`
Extract text from a PDF.

**Parameters**:
- `pdf_path` (string, required) - Path to PDF
- `pages` (array, optional) - Page range [start, end]

**Returns**:
```json
{
  "path": "/path/to/paper.pdf",
  "text": "Extracted text content...",
  "pages_extracted": "1-5",
  "word_count": 2341
}
```

**Example**:
> "Extract text from the first 5 pages of paper.pdf"

#### `pdf_search`
Search across PDF files.

**Parameters**:
- `query` (string, required) - Search term
- `limit` (integer, optional) - Max results (default: 10)

**Returns**:
```json
{
  "results": [
    {
      "path": "/path/to/paper.pdf",
      "title": "Statistical Mediation Analysis",
      "score": 0.87,
      "context": "...bootstrap confidence intervals...",
      "page": 12
    }
  ],
  "count": 1
}
```

**Example**:
> "Search my PDFs for bootstrap methods"

### Writing Domain (3 tools)

#### `manuscript_list`
List all manuscripts.

**Parameters**: None

**Returns**:
```json
{
  "manuscripts": [
    {
      "path": "/path/to/manuscripts/mediation-paper",
      "title": "Mediation in Causal Models",
      "status": "under_review",
      "target": "Psychometrika",
      "progress": 90
    }
  ],
  "count": 1
}
```

**Example**:
> "What manuscripts am I working on?"

#### `manuscript_status`
Get manuscript status.

**Parameters**:
- `manuscript_name` (string, required) - Manuscript directory name

**Returns**:
```json
{
  "title": "Mediation in Causal Models",
  "status": "under_review",
  "target": "Psychometrika",
  "progress": 90,
  "next_action": "Revise based on reviewer comments",
  "files": ["paper.tex", "references.bib", "figures/"]
}
```

**Example**:
> "What's the status of my mediation paper?"

#### `bib_check`
Check bibliography completeness.

**Parameters**:
- `manuscript_dir` (string, required) - Manuscript directory
- `bib_file` (string, optional) - Bibliography file name

**Returns**:
```json
{
  "manuscript": "mediation-paper",
  "total_citations": 47,
  "missing_keys": ["smith2020", "jones2019"],
  "unused_keys": ["oldpaper1990"],
  "status": "incomplete"
}
```

**Example**:
> "Check if my bibliography is complete for the mediation paper"

### Unified Search (2 tools)

#### `unified_search`
Search across all sources.

**Parameters**:
- `query` (string, required) - Search term
- `sources` (array, optional) - Sources to search: ["vault", "zotero", "pdf"]
- `limit` (integer, optional) - Results per source

**Returns**:
```json
{
  "vault": [...],
  "zotero": [...],
  "pdf": [...],
  "total_results": 23
}
```

**Example**:
> "Search everywhere for mediation analysis"

#### `vault_stats`
Get vault statistics.

**Parameters**: None

**Returns**:
```json
{
  "total_notes": 342,
  "total_links": 1247,
  "total_tags": 89,
  "avg_links_per_note": 3.6,
  "most_linked": [
    {"note": "Causal Inference", "links": 45},
    {"note": "Mediation Analysis", "links": 32}
  ]
}
```

**Example**:
> "What are my vault statistics?"

## Usage Patterns

### Claude Desktop

Simply ask Claude natural language questions:

```
You: "Search my vault for notes about statistical power"

Claude: I'll search your vault for notes about statistical power.
[Calls vault_search tool with query="statistical power"]

Found 5 notes about statistical power:
1. Statistical Power Basics (Concepts/)
2. Power Analysis for Mediation (Methods/)
3. Sample Size Determination (Planning/)
...
```

### Claude Code CLI

Claude Code automatically uses MCP tools when relevant:

```
You: "What papers do I have on causal inference?"

Claude: Let me search your Zotero library...
[Calls zotero_search tool]

I found 23 papers on causal inference in your library.
Here are the most recent:
...
```

### Combining Tools

Claude can chain multiple tools:

```
You: "Find papers on mediation and create a literature note"

Claude: 
1. [Calls zotero_search] Found baron1986
2. [Calls zotero_get] Retrieved full details
3. [Creates literature note in vault]

I've created a literature note at Literature/baron1986.md
```

## Advanced Usage

### Filtering Results

```
"Search my vault for notes about mediation, limit to 5 results"
[vault_search with limit=5]
```

### Case-Sensitive Search

```
"Search for 'Mediation' (case-sensitive) in my vault"
[vault_search with case_sensitive=true]
```

### Specific Fields

```
"Find papers by MacKinnon in Zotero"
[zotero_search with field="author"]
```

### Graph Analysis

```
"Generate a graph of my 50 most connected notes with tags"
[vault_graph with limit=50, include_tags=true]
```

### PDF Processing

```
"Extract text from pages 10-20 of paper.pdf"
[pdf_extract with pages=[10, 20]]
```

## Error Handling

Tools return error messages in a consistent format:

```json
{
  "error": "Note not found",
  "details": "No note matching 'Nonexistent Note'",
  "suggestions": [
    "Check note title spelling",
    "Use vault_list to see available notes"
  ]
}
```

## Debugging

Enable debug mode in Claude Code:

```json
{
  "debug": true,
  "mcpServers": {
    "nexus": {
      ...
    }
  }
}
```

Check MCP server logs:
```bash
tail -f ~/.claude/mcp-server-nexus.log
```

## Best Practices

### 1. Be Specific

```
❌ "Search for papers"
✅ "Search my Zotero library for papers on mediation by MacKinnon"
```

### 2. Use Limits

```
❌ "List all my notes" (might be thousands)
✅ "List 10 recently modified notes"
```

### 3. Combine Tools

```
✅ "Find papers on mediation in Zotero, then search my vault for related notes"
```

### 4. Verify Results

```
✅ "Search for 'bootstrap' in PDFs and show the top 3 matches with context"
```

## Limitations

- **Read-only**: MCP tools don't modify your data (search/read only)
- **Rate limits**: No artificial limits, but operations take time
- **Context**: Each tool call is stateless
- **Dependencies**: Requires configured Nexus installation

## Troubleshooting

### "MCP server not responding"

Check configuration:
```bash
cat ~/.claude/settings.json
```

Verify Nexus works:
```bash
nexus doctor
```

### "Tool returned error"

Check the error message:
- File not found → Verify paths
- Database locked → Close Zotero
- Permission denied → Check file permissions

### "Unexpected results"

Try the CLI command directly:
```bash
nexus research zotero search "query"
```

## See Also

- [CLI Reference](cli.md) - Command-line interface
- [Python API](api.md) - Python library
- [Tutorials](../tutorials/first-steps.md) - Getting started guides
