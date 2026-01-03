---
name: nexus:search
description: Search across all domains (vault, Zotero, manuscripts)
---

# Unified Search

I'll search across your knowledge base, literature, and manuscripts.

**Usage:** `/nexus:search <query>`

<system>
This command performs a unified search across all Nexus domains.

## Implementation

For a given query, search across:

1. **Knowledge vault**: `nexus knowledge search "QUERY" --json`
2. **Zotero library**: `nexus research zotero search "QUERY" --json`
3. **Manuscripts**: `nexus write manuscript search "QUERY" --json`
4. **Bibliography entries**: Search .bib files in manuscript directories

## Execution

```bash
QUERY="$1"

echo "=== Vault Notes ==="
nexus knowledge search "$QUERY" --limit 5 2>/dev/null

echo ""
echo "=== Zotero Library ==="
nexus research zotero search "$QUERY" --limit 5 2>/dev/null

echo ""
echo "=== Manuscripts ==="
nexus write manuscript search "$QUERY" 2>/dev/null
```

## Output Format

```
═══════════════════════════════════════════════════
              SEARCH: "mediation analysis"
═══════════════════════════════════════════════════

📝 VAULT NOTES (12 matches)
────────────────────────────────────────
• 10-PROJECTS/mediation-planning.md
  "...indirect effects in mediation analysis..."
• 20-AREAS/causal-inference/mediation.md
  "...modern mediation analysis methods..."
• 30-RESOURCES/literature/MacKinnon2008.md
  "...comprehensive mediation analysis guide..."

📚 ZOTERO (47 matches)
────────────────────────────────────────
• MacKinnon (2008) - Introduction to Statistical Mediation Analysis
• VanderWeele (2015) - Explanation in Causal Inference
• Imai (2010) - A General Approach to Causal Mediation Analysis

📖 MANUSCRIPTS (2 matches)
────────────────────────────────────────
• product-of-three - Product of Three Normal Variables
• sensitivity - Sensitivity Analysis for Mediation
```

## Follow-up Actions

Based on results, offer:
1. **Open note**: For vault matches
2. **Get citation**: For Zotero matches
3. **Show manuscript**: For manuscript matches
4. **Narrow search**: Add filters or more specific terms
</system>
