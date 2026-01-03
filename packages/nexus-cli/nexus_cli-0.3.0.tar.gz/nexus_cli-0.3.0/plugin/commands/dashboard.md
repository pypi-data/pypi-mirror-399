---
name: nexus:dashboard
description: Show unified dashboard of all domains
---

# Nexus Dashboard

I'll show you a unified view of your current status across all domains.

## Running Dashboard

```bash
# Knowledge stats
echo "=== Knowledge ==="
nexus knowledge stats 2>/dev/null || echo "Vault not configured"

# Active manuscripts
echo ""
echo "=== Manuscripts ==="
nexus write manuscript active 2>/dev/null || echo "No active manuscripts"

# Active courses
echo ""
echo "=== Courses ==="
nexus teach course list 2>/dev/null || echo "No courses found"

# Recent Zotero additions
echo ""
echo "=== Recent Literature ==="
nexus research zotero recent --days 7 2>/dev/null || echo "Zotero not configured"
```

<system>
This command provides a unified dashboard view across all Nexus domains.

## Implementation

Run each domain's summary command and aggregate the output:

1. **Knowledge Stats**: `nexus knowledge stats`
2. **Active Manuscripts**: `nexus write manuscript active`
3. **Course List**: `nexus teach course list`
4. **Recent Literature**: `nexus research zotero recent --days 7`

For each section, gracefully handle missing configuration or empty results.

## Output Format

Present as a clean dashboard with sections:

```
═══════════════════════════════════════════════════
                    NEXUS DASHBOARD
═══════════════════════════════════════════════════

📚 KNOWLEDGE VAULT
────────────────────────────────────────
Notes: 1,234
Recent: 15 modified this week

📝 MANUSCRIPTS (Active: 3)
────────────────────────────────────────
🔥 collider          [████████░░] 80%  → Under review at Biostatistics
📝 product-of-three  [██████░░░░] 60%  → Revise discussion section
✏️ sensitivity       [████░░░░░░] 40%  → Complete simulation code

📖 COURSES (Active: 2)
────────────────────────────────────────
🔥 stat-440  Week 7/15  [██████████░░░░░] 47%
🔥 stat-579  Week 5/16  [██████░░░░░░░░░] 31%

📑 RECENT LITERATURE (Last 7 days: 5)
────────────────────────────────────────
• VanderWeele (2024) - Sensitivity Analysis...
• MacKinnon (2024) - Mediation Methods...
```

## Follow-up Actions

Offer to:
- Drill into any domain (`/nexus:manuscripts`, `/nexus:courses`)
- Run health check (`nexus doctor`)
- Search across domains
</system>
