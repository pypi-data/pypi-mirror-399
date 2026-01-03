---
name: nexus:cite
description: Quick citation lookup and formatting
---

# Citation Lookup

I'll find and format citations from your Zotero library.

**Usage:** `/nexus:cite <search_query>` or `/nexus:cite <item_key>`

**Examples:**
- `/nexus:cite MacKinnon 2008` - Search for paper
- `/nexus:cite ABC123XYZ` - Get specific item by key

<system>
This command provides quick citation lookup and formatting.

## Implementation

1. First, determine if input is a Zotero key or search query
2. For key: `nexus research zotero cite KEY --format bibtex`
3. For search: `nexus research zotero search "QUERY" --json`

```bash
INPUT="$1"

# Check if it looks like a Zotero key (alphanumeric, 8 chars)
if [[ "$INPUT" =~ ^[A-Z0-9]{8}$ ]]; then
    # Direct key lookup
    nexus research zotero cite "$INPUT" --format apa
    echo ""
    echo "BibTeX:"
    nexus research zotero cite "$INPUT" --format bibtex
else
    # Search
    nexus research zotero search "$INPUT" --limit 5
fi
```

## Output Format

For search results:
```
═══════════════════════════════════════════════════
              CITATION SEARCH: "MacKinnon 2008"
═══════════════════════════════════════════════════

Found 3 matches:

1. [ABC123XY] MacKinnon, D. P. (2008)
   Introduction to Statistical Mediation Analysis
   Lawrence Erlbaum Associates
   DOI: 10.4324/9780203809556

2. [DEF456ZW] MacKinnon, D. P., Fairchild, A. J., & Fritz, M. S. (2007)
   Mediation Analysis
   Annual Review of Psychology, 58, 593-614
   DOI: 10.1146/annurev.psych.58.110405.085542

3. [GHI789AB] MacKinnon, D. P., Lockwood, C. M., & Williams, J. (2004)
   Confidence Limits for the Indirect Effect
   Multivariate Behavioral Research, 39(1), 99-128

────────────────────────────────────────
💡 Use: /nexus:cite ABC123XY for full citation
```

For direct key lookup:
```
═══════════════════════════════════════════════════
              CITATION: ABC123XY
═══════════════════════════════════════════════════

📖 APA Format:
MacKinnon, D. P. (2008). Introduction to Statistical Mediation Analysis.
Lawrence Erlbaum Associates. https://doi.org/10.4324/9780203809556

📝 BibTeX:
@book{MacKinnon2008,
  author = {MacKinnon, David P.},
  title = {Introduction to Statistical Mediation Analysis},
  publisher = {Lawrence Erlbaum Associates},
  year = {2008},
  doi = {10.4324/9780203809556}
}

────────────────────────────────────────
📋 Copied to clipboard: @MacKinnon2008
```

## Follow-up Actions

1. **Copy citation key**: For use in manuscript
2. **Export to .bib file**: Append to manuscript bibliography
3. **Find related papers**: Search for papers that cite this one
4. **Open in Zotero**: Open the item in Zotero app
</system>
