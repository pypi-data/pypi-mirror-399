---
name: nexus:manuscripts
description: Show manuscript status and manage writing projects
---

# Manuscript Management

I'll show your manuscript status and help with writing workflows.

## Quick Status

```bash
# Active manuscripts with progress
nexus write manuscript active

# Deadlines coming up
nexus write manuscript deadlines
```

<system>
This command provides manuscript management functionality.

## Implementation

1. **List active manuscripts**: `nexus write manuscript active --json`
2. **Show deadlines**: `nexus write manuscript deadlines --json`
3. **Get statistics**: `nexus write manuscript stats --json`

## Display Format

```
═══════════════════════════════════════════════════
                    MANUSCRIPTS
═══════════════════════════════════════════════════

📊 ACTIVE (3 manuscripts)
────────────────────────────────────────
🔥 collider
   [████████░░░░░░░░░░░░] 80%  •  ~9,967 words
   Target: Biostatistics  •  Status: Under review
   Next: Address reviewer comments

📝 product-of-three
   [████████████░░░░░░░░] 60%  •  ~4,200 words
   Target: JASA  •  Status: Draft
   Next: Revise discussion section

✏️ sensitivity
   [████████░░░░░░░░░░░░] 40%  •  ~2,100 words
   Target: Epidemiology  •  Status: Revision
   Next: Complete simulation code

⏰ DEADLINES
────────────────────────────────────────
• product-of-three → JASA submission (Jan 15, 2025)
• sensitivity → Conference deadline (Feb 1, 2025)
```

## Available Actions

Offer these follow-up actions:
1. **Show details**: `nexus write manuscript show NAME`
2. **Check citations**: `nexus write bib check PATH`
3. **Open in editor**: Navigate to manuscript directory
4. **Build**: `nexus teach quarto build PATH` (if Quarto)

## Drill-Down

If user asks about a specific manuscript:
```bash
nexus write manuscript show MANUSCRIPT_NAME --json
nexus write bib check ~/projects/research/MANUSCRIPT_NAME --json
```
</system>
