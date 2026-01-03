# Zotero Integration Tutorial

Learn how to connect Nexus CLI to your Zotero library for powerful literature management and citation workflows.

## Prerequisites

- Zotero desktop app installed
- A populated Zotero library
- Nexus CLI installed and configured

## Step 1: Locate Your Zotero Database

Zotero stores your library in an SQLite database. Find it:

### macOS
```bash
~/Zotero/zotero.sqlite
```

### Linux
```bash
~/.zotero/zotero/zotero.sqlite
```

### Windows
```
C:\Users\YourName\Zotero\zotero.sqlite
```

Verify it exists:
```bash
ls -lh ~/Zotero/zotero.sqlite
```

## Step 2: Configure Nexus

Edit your Nexus config:

```bash
nexus config --edit
```

Add/update the Zotero section:

```yaml
zotero:
  database: /Users/username/Zotero/zotero.sqlite
  storage: /Users/username/Zotero/storage
```

## Step 3: Verify Connection

Check that Nexus can access your Zotero library:

```bash
nexus doctor
```

Look for:
```
Zotero
  ✓ Database found
  ✓ Database readable
  ✓ Storage directory accessible
```

## Step 4: Explore Your Library

### Search for Papers

```bash
# Basic search
nexus research zotero search "mediation"

# Limit results
nexus research zotero search "causal inference" --limit 5

# Search specific fields
nexus research zotero search "baron" --field author
nexus research zotero search "2020" --field year
```

### View Recent Additions

```bash
# Last 10 items added
nexus research zotero recent --limit 10

# Last 20 items
nexus research zotero recent -n 20
```

### Get Paper Details

```bash
# By citation key
nexus research zotero get baron1986

# With full details
nexus research zotero get mackinnon2007 --full
```

## Step 5: Generate Citations

### APA Format

```bash
nexus research zotero cite baron1986 --format apa
```

Output:
```
Baron, R. M., & Kenny, D. A. (1986). The moderator-mediator variable 
distinction in social psychological research: Conceptual, strategic, 
and statistical considerations. Journal of Personality and Social 
Psychology, 51(6), 1173-1182.
```

### BibTeX Format

```bash
nexus research zotero cite mackinnon2007 --format bibtex
```

Output:
```bibtex
@book{mackinnon2007,
  title = {Introduction to Statistical Mediation Analysis},
  author = {MacKinnon, David P.},
  year = {2007},
  publisher = {Routledge},
  address = {New York, NY}
}
```

### Batch Citations

```bash
# Multiple citations
nexus research zotero cite baron1986 mackinnon2007 hayes2013
```

## Step 6: Advanced Searching

### By Collection

```bash
# List collections
nexus research zotero collections

# Search within a collection
nexus research zotero search "mediation" --collection "Causal Inference"
```

### By Tag

```bash
# List all tags
nexus research zotero tags

# Search by tag
nexus research zotero search --tag "methods"
nexus research zotero search --tag "review"
```

### By Year Range

```bash
# Papers from 2020-2023
nexus research zotero search --year-min 2020 --year-max 2023
```

### Combined Filters

```bash
# Recent papers on mediation with tag "methods"
nexus research zotero search "mediation" \
  --tag methods \
  --year-min 2020 \
  --limit 10
```

## Step 7: Export for Other Tools

### JSON Output

Perfect for piping to other tools:

```bash
# Search and save as JSON
nexus research zotero search "causal" --json > causal-papers.json

# Recent papers as JSON
nexus research zotero recent --limit 50 --json > recent.json
```

### Process with jq

```bash
# Extract just titles
nexus research zotero search "mediation" --json | jq -r '.[].title'

# Count papers by year
nexus research zotero search "causal" --json | \
  jq -r '.[].year' | sort | uniq -c

# Filter by multiple criteria
nexus research zotero recent --json | \
  jq '[.[] | select(.year > 2020 and .type == "journalArticle")]'
```

## Integration Workflows

### Workflow 1: Literature Review

```bash
# 1. Search for papers
nexus research zotero search "mediation analysis" --json > papers.json

# 2. Extract titles and abstracts
jq -r '.[] | "\(.title)\n\(.abstract)\n"' papers.json > abstracts.txt

# 3. Use Claude to summarize (if you have Claude CLI)
cat abstracts.txt | claude -p "Summarize these papers on mediation"
```

### Workflow 2: Citation Management

```bash
# 1. Find papers you need to cite
nexus research zotero search "baron kenny" --limit 5

# 2. Generate citations
nexus research zotero cite baron1986 mackinnon2007 --format apa > refs.txt

# 3. Add to manuscript
cat refs.txt >> manuscript/references.md
```

### Workflow 3: Building a Reading List

```bash
# 1. Get recent papers in your field
nexus research zotero recent --limit 20 --json > reading-list.json

# 2. Filter to unread papers
jq '[.[] | select(.read == false)]' reading-list.json > unread.json

# 3. Create markdown reading list
jq -r '.[] | "- [ ] \(.title) (\(.year))"' unread.json > to-read.md
```

### Workflow 4: Creating Literature Notes

For each paper, create an Obsidian note:

```bash
#!/bin/bash
# create-lit-note.sh

KEY=$1
PAPER=$(nexus research zotero get $KEY --json)

TITLE=$(echo $PAPER | jq -r '.title')
AUTHOR=$(echo $PAPER | jq -r '.author')
YEAR=$(echo $PAPER | jq -r '.year')

cat > "Literature/${KEY}.md" <<EOF
---
title: $TITLE
author: $AUTHOR
year: $YEAR
zotero_key: $KEY
tags: [literature]
---

# $TITLE

**Citation**: @$KEY

## Summary

## Key Points

## Connections

---

**Full Citation**:
$(nexus research zotero cite $KEY --format apa)
EOF

echo "Created Literature/${KEY}.md"
```

Usage:
```bash
./create-lit-note.sh baron1986
```

## Best Practices

### 1. Keep Zotero Running

Nexus reads directly from the database, but keep Zotero closed while running Nexus commands to avoid database locks.

### 2. Use Consistent Citation Keys

Zotero generates keys automatically, but you can customize them in Zotero preferences:
- Format: `[auth][year]`
- Example: `baron1986`, `mackinnon2007`

### 3. Tag Strategically

Use tags to categorize papers:
- `methods` - Methodological papers
- `review` - Review articles  
- `theory` - Theoretical work
- `application` - Applied research
- `to-read` - Reading queue

### 4. Maintain Collections

Organize papers into collections:
- By project
- By topic
- By status (reading, read, cite)

### 5. Add Notes in Zotero

Nexus can access notes you add in Zotero:
```bash
nexus research zotero get baron1986 --notes
```

## Combining with PDFs

If you have PDFs attached to Zotero items:

```bash
# Find Zotero storage directory
ls ~/Zotero/storage/

# Search PDF content
nexus research pdf search "bootstrap" --directories ~/Zotero/storage
```

Configure in `config.yaml`:
```yaml
pdf:
  directories:
    - ~/Zotero/storage
    - ~/Documents/PDFs
```

## Troubleshooting

### "Database is locked"

Zotero is running. Close it and try again:
```bash
# macOS: Quit Zotero
# Then retry command
nexus research zotero search "test"
```

### "No results found"

Check that:
1. Your search term is spelled correctly
2. The database path is correct: `nexus doctor`
3. Your library actually contains matching items

### "Permission denied"

```bash
# Check database permissions
ls -l ~/Zotero/zotero.sqlite

# Should be readable
chmod u+r ~/Zotero/zotero.sqlite
```

## Next Steps

- **Graph Visualization**: [Visualize paper connections](graph-viz.md)
- **Writing Integration**: [Link citations to manuscripts](../guide/writing.md)
- **Vault Integration**: [Connect Zotero to Obsidian](vault-setup.md)

## Resources

- [Zotero Documentation](https://www.zotero.org/support/)
- [Better BibTeX Plugin](https://retorque.re/zotero-better-bibtex/)
- [Zotero Citation Styles](https://www.zotero.org/styles)
