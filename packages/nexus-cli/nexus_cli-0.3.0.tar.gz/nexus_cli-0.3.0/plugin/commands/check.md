---
name: nexus:check
description: Run health checks on manuscript citations
---

# Citation Check

I'll check your manuscript for citation issues.

**Usage:** `/nexus:check <manuscript_name>` or `/nexus:check` (in manuscript directory)

<system>
This command checks manuscript citations for common issues.

## Implementation

```bash
MANUSCRIPT="$1"

# Determine manuscript path
if [[ -n "$MANUSCRIPT" ]]; then
    # Search for manuscript
    MS_PATH=$(nexus write manuscript show "$MANUSCRIPT" --json 2>/dev/null | jq -r '.path')
else
    # Use current directory
    MS_PATH="$(pwd)"
fi

if [[ -z "$MS_PATH" ]] || [[ ! -d "$MS_PATH" ]]; then
    echo "Error: Could not find manuscript"
    exit 1
fi

# Run citation check
nexus write bib check "$MS_PATH" --json
```

## Output Format

```
═══════════════════════════════════════════════════
         CITATION CHECK: collider
═══════════════════════════════════════════════════

📊 SUMMARY
────────────────────────────────────────
Citations in text:    112
Bibliography entries: 334
Status:               ⚠️ Issues found

❌ MISSING CITATIONS (2)
────────────────────────────────────────
These keys are cited but not in your .bib file:

  • @VanderWeele2020a
    Used in: _manuscript/index.qmd (line 234)

  • @Imai2013
    Used in: _manuscript/index.qmd (line 456)

💡 Suggestions:
  → nexus research zotero search "VanderWeele 2020"
  → nexus research zotero search "Imai 2013"

⚠️ UNUSED ENTRIES (223)
────────────────────────────────────────
These entries are in .bib but not cited:

  • @MacKinnon2000
  • @Baron1986
  • @Sobel1982
  ... and 220 more

💡 Consider removing unused entries before submission.

────────────────────────────────────────
✅ All cited references have valid entries: NO
🔧 Run: nexus write bib check PATH --fix to auto-fix
```

## Check Types

1. **Missing citations**: Keys in text but not in .bib
2. **Unused entries**: Keys in .bib but not in text
3. **Duplicate keys**: Same key defined multiple times
4. **Format issues**: Malformed BibTeX entries

## Follow-up Actions

1. **Search Zotero for missing**: Find and add missing references
2. **Clean unused entries**: Remove or archive unused refs
3. **Open manuscript**: Navigate to manuscript for editing
4. **Rebuild bibliography**: Export fresh from Zotero
</system>
