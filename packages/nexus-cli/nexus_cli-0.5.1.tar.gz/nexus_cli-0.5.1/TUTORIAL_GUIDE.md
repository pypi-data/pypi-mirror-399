# Nexus Interactive Tutorial System

## Overview

Nexus includes a built-in interactive tutorial system to help new users learn the CLI at their own pace. Tutorials are organized into three levels:

- **Getting Started** (7 steps) - Basic commands and configuration
- **Medium** (11 steps) - Domain-specific workflows
- **Advanced** (12 steps) - Batch operations and integrations

## Quick Start

```bash
# List all available tutorials
nexus learn

# Run the Getting Started tutorial
nexus learn getting-started

# Run the Medium tutorial
nexus learn medium

# Run the Advanced tutorial
nexus learn advanced
```

## Tutorial Levels

### 1. Getting Started (7 steps)

**Target Audience:** First-time users, those setting up Nexus

**Topics Covered:**
1. Introduction to Nexus architecture
2. Health check with `nexus doctor`
3. Viewing configuration with `nexus config`
4. Understanding command structure
5. First Zotero search
6. JSON output for automation
7. Next steps and resources

**Duration:** ~10-15 minutes

**Prerequisites:** Nexus installed, basic terminal knowledge

### 2. Medium - Domain Workflows (11 steps)

**Target Audience:** Users comfortable with basics, ready to explore specific domains

**Topics Covered:**

**Research Workflow (4 steps):**
- Literature discovery with Zotero search
- Getting paper details
- Generating citations (APA, BibTeX)
- Exploring and filtering by tags

**Knowledge Workflow (3 steps):**
- Vault search across all notes
- Reading notes with frontmatter
- Graph analysis and statistics

**Teaching Workflow (1 step):**
- Course overview and tracking

**Writing Workflow (1 step):**
- Manuscript tracking and status

**Unified Search (1 step):**
- Cross-domain search (Zotero + Vault + PDFs)

**Duration:** ~20-30 minutes

**Prerequisites:** Completed Getting Started tutorial

### 3. Advanced - Power User Techniques (12 steps)

**Target Audience:** Experienced users ready for automation and batch operations

**Topics Covered:**

**Batch Operations (4 steps):**
- Batch status updates for manuscripts
- Batch progress tracking
- Metadata export (JSON/CSV)
- Archiving multiple manuscripts

**Graph Visualization (2 steps):**
- GraphML export for Gephi/Cytoscape
- D3.js export for web visualizations

**Integration Patterns (4 steps):**
- JSON pipelines with Claude
- Bibliography citation checking
- Quarto project automation
- Dependency checking

**Custom Workflows (2 steps):**
- Combining commands
- Building personal automation patterns

**Duration:** ~30-40 minutes

**Prerequisites:** Completed Medium tutorial, familiarity with JSON and shell scripting helpful

## Interactive Features

### Progress Tracking
Each tutorial tracks your progress through steps. You can:
- Continue to the next step
- Pause and resume later (with `--step` flag)
- Skip ahead if needed

### Hands-On Learning
Most steps include:
- **Command examples** - Actual commands to try
- **Interactive prompts** - Confirm you've tried each command
- **Hints** - Additional context and tips
- **Real-world use cases** - Practical applications

### Resuming Tutorials

If you pause a tutorial, you can resume from a specific step:

```bash
# Resume Getting Started from step 4
nexus learn getting-started --step 4

# Resume Medium from step 7
nexus learn medium --step 7
```

## Tutorial Structure

Each tutorial follows this pattern:

1. **Introduction** - Overview and learning objectives
2. **Sequential Steps** - Guided hands-on exercises
3. **Interactive Prompts** - Confirm understanding before proceeding
4. **Completion Summary** - Key takeaways and next steps

## Example Tutorial Session

```bash
$ nexus learn getting-started

╭──────────────────────── 🎓 Nexus Tutorial ────────────────────────╮
│ Getting Started with Nexus                                        │
│ Learn the basics of Nexus CLI - your knowledge workflow companion │
│                                                                   │
│ Level: Getting Started                                            │
│ Steps: 7                                                          │
╰───────────────────────────────────────────────────────────────────╯

Ready to start? [y/n] (y): y

╭─────────────────── Step 1/7 ────────────────────╮
│ Welcome to Nexus!                               │
│                                                 │
│ Nexus is a CLI tool for academic researchers.  │
│ It connects:                                    │
│ • 🔬 Research (Zotero, PDFs, literature)       │
│ • 📚 Teaching (Courses, Quarto materials)      │
│ • ✍️ Writing (Manuscripts, LaTeX, bibliography)│
│ • 🧠 Knowledge (Obsidian vault, search)        │
│                                                 │
│ Think of it as the 'body' that Claude (the     │
│ brain) uses to access your work.               │
╰─────────────────────────────────────────────────╯

Continue to next step? [y/n] (y): y

╭─────────────────── Step 2/7 ────────────────────╮
│ Check Your Installation                         │
│                                                 │
│ First, let's verify that Nexus can access      │
│ your tools and data. The 'doctor' command      │
│ checks for Zotero, your vault, R, Quarto, and  │
│ more.                                           │
╰─────────────────────────────────────────────────╯

Command to try:
  nexus doctor

💡 Hint: This shows which components are available. Don't worry if some are missing!

Have you tried this command? [y/n] (y): y
...
```

## Best Practices for Using Tutorials

### For New Users
1. **Start with Getting Started** - Don't skip the basics
2. **Follow along in a terminal** - Actually run the commands
3. **Take your time** - Understand each step before moving on
4. **Experiment** - Try variations of the commands shown

### For Intermediate Users
1. **Jump to Medium** - If basics are familiar, start here
2. **Focus on relevant domains** - Pay special attention to research/teaching/writing steps that match your work
3. **Take notes** - Build your own cheat sheet of useful commands

### For Advanced Users
1. **Review Advanced tutorial** - Even if you know the CLI, learn batch operations
2. **Adapt examples** - Modify commands for your specific workflows
3. **Build automation** - Use tutorial patterns to create shell scripts or aliases

## Tips for Claude Integration

The tutorials are designed with Claude integration in mind:

1. **JSON Output Everywhere** - Most commands support `--json` for piping to Claude
2. **Structured Data** - Output is designed for AI parsing and analysis
3. **Example Workflows** - Advanced tutorial shows Claude integration patterns

Example Claude workflow from tutorials:
```bash
# Get recent papers in JSON
nexus research zotero recent --limit 10 --json > papers.json

# Analyze with Claude (if you have claude CLI)
cat papers.json | claude -p "Summarize these papers by theme"
```

## Troubleshooting

### Tutorial Won't Start
- Check installation: `nexus --version`
- Verify tutorial exists: `nexus learn`
- Use correct level name: `getting-started`, `medium`, or `advanced`

### Commands Fail During Tutorial
- Run `nexus doctor` to check component availability
- Some commands require Zotero, vault, or other components
- Tutorial will guide you even if components are missing

### Want to Skip Steps
- Use `--step N` flag to jump to specific step
- Remember step numbers are 1-indexed

## What's Next?

After completing all tutorials:

1. **Explore the docs** - Check `docs/` directory for detailed references
2. **Review command help** - Each command has `--help` for details
3. **Join the community** - Report issues or contribute at GitHub
4. **Build workflows** - Create custom scripts using what you've learned

## Tutorial Philosophy

These tutorials follow these principles:

- **Learn by doing** - Active commands, not passive reading
- **Progressive complexity** - Build from simple to advanced
- **Real-world focus** - Use actual research workflows, not toy examples
- **Integration-first** - Designed for Claude and automation from the start
- **Self-paced** - Pause, resume, skip - you're in control

## Contributing

Want to improve the tutorials? Suggestions welcome:

1. Report issues at GitHub
2. Suggest new tutorial topics
3. Share your custom workflows
4. Contribute example use cases

---

**Happy Learning!** 🎓

Start your journey: `nexus learn getting-started`
