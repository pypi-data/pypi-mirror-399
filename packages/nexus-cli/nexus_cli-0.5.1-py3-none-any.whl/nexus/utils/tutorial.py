"""
Interactive tutorial system for Nexus CLI.

Provides guided learning experiences at three levels:
- Getting Started: Basic commands and configuration
- Medium: Domain-specific workflows (research, teaching, writing)
- Advanced: Integration patterns and batch operations
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


class TutorialLevel(str, Enum):
    """Tutorial difficulty levels."""

    GETTING_STARTED = "getting-started"
    MEDIUM = "medium"
    ADVANCED = "advanced"


@dataclass
class TutorialStep:
    """A single step in the tutorial."""

    title: str
    description: str
    command: str | None = None
    interactive: bool = False
    validator: Callable[[], bool] | None = None
    hint: str | None = None


class Tutorial:
    """Base tutorial class."""

    def __init__(self, name: str, level: TutorialLevel, description: str):
        self.name = name
        self.level = level
        self.description = description
        self.steps: list[TutorialStep] = []
        self.current_step = 0

    def add_step(self, step: TutorialStep) -> None:
        """Add a step to the tutorial."""
        self.steps.append(step)

    def show_intro(self) -> None:
        """Show tutorial introduction."""
        level_colors = {
            TutorialLevel.GETTING_STARTED: "green",
            TutorialLevel.MEDIUM: "yellow",
            TutorialLevel.ADVANCED: "red",
        }

        color = level_colors.get(self.level, "blue")

        console.print()
        console.print(
            Panel.fit(
                f"[bold]{self.name}[/]\n"
                f"[dim]{self.description}[/]\n\n"
                f"[{color}]Level: {self.level.value.replace('-', ' ').title()}[/]\n"
                f"[dim]Steps: {len(self.steps)}[/]",
                border_style=color,
                title="🎓 Nexus Tutorial",
            )
        )
        console.print()

    def show_step(self, step_num: int) -> None:
        """Show a tutorial step."""
        if step_num >= len(self.steps):
            return

        step = self.steps[step_num]

        console.print(
            Panel(
                f"[bold]{step.title}[/]\n\n{step.description}",
                border_style="blue",
                title=f"Step {step_num + 1}/{len(self.steps)}",
            )
        )

        if step.command:
            console.print(f"\n[dim]Command to try:[/]")
            console.print(f"  [cyan]{step.command}[/]")

        if step.hint:
            console.print(f"\n[dim]💡 Hint:[/] {step.hint}")

        console.print()

    def run(self) -> None:
        """Run the interactive tutorial."""
        self.show_intro()

        if not Confirm.ask("Ready to start?", default=True):
            console.print("[yellow]Tutorial cancelled.[/]")
            return

        console.print()

        for i, step in enumerate(self.steps):
            self.current_step = i
            self.show_step(i)

            if step.interactive:
                if not Confirm.ask("Have you tried this command?", default=True):
                    if step.hint:
                        console.print(f"\n[dim]{step.hint}[/]\n")
                    Prompt.ask("Press Enter when ready to continue")

            if i < len(self.steps) - 1:
                if not Confirm.ask("Continue to next step?", default=True):
                    console.print("\n[yellow]Tutorial paused.[/]")
                    console.print(f"[dim]Resume with:[/] nexus learn {self.level.value} --step {i + 2}")
                    return

            console.print()

        self.show_completion()

    def show_completion(self) -> None:
        """Show tutorial completion message."""
        console.print(
            Panel.fit(
                "[bold green]✓ Tutorial Complete![/]\n\n"
                f"You've finished the [cyan]{self.name}[/] tutorial.\n"
                "Great job!",
                border_style="green",
            )
        )


# ─────────────────────────────────────────────────────────────────────────────
# Getting Started Tutorial
# ─────────────────────────────────────────────────────────────────────────────


def create_getting_started_tutorial() -> Tutorial:
    """Create the Getting Started tutorial."""
    tutorial = Tutorial(
        name="Getting Started with Nexus",
        level=TutorialLevel.GETTING_STARTED,
        description="Learn the basics of Nexus CLI - your knowledge workflow companion",
    )

    tutorial.add_step(
        TutorialStep(
            title="Welcome to Nexus!",
            description=(
                "Nexus is a CLI tool for academic researchers. It connects:\n"
                "• 🔬 Research (Zotero, PDFs, literature)\n"
                "• 📚 Teaching (Courses, Quarto materials)\n"
                "• ✍️ Writing (Manuscripts, LaTeX, bibliography)\n"
                "• 🧠 Knowledge (Obsidian vault, search)\n\n"
                "Think of it as the 'body' that Claude (the brain) uses to access your work."
            ),
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Check Your Installation",
            description=(
                "First, let's verify that Nexus can access your tools and data.\n"
                "The 'doctor' command checks for Zotero, your vault, R, Quarto, and more."
            ),
            command="nexus doctor",
            interactive=True,
            hint="This shows which components are available. Don't worry if some are missing!",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="View Your Configuration",
            description=("Nexus stores your settings in ~/.config/nexus/config.yaml\nLet's see what's configured."),
            command="nexus config",
            interactive=True,
            hint="This shows paths to your Zotero database, Obsidian vault, and more.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Explore the Command Structure",
            description=(
                "Nexus organizes commands by domain:\n"
                "• nexus research - Work with Zotero and PDFs\n"
                "• nexus teach - Manage courses and materials\n"
                "• nexus write - Handle manuscripts and bibliography\n"
                "• nexus knowledge - Search vault and notes\n"
                "• nexus integrate - Connect with aiterm, R, Git"
            ),
            command="nexus --help",
            interactive=True,
            hint="Each domain has subcommands. Try: nexus research --help",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Your First Search",
            description=(
                "Let's search your Zotero library!\n"
                "This is one of the most powerful features - finding papers instantly."
            ),
            command="nexus research zotero search mediation --limit 5",
            interactive=True,
            hint="Replace 'mediation' with any topic you're researching.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Understanding JSON Output",
            description=(
                "Most commands support --json for machine-readable output.\n"
                "This is perfect for piping to Claude or other tools."
            ),
            command="nexus research zotero recent --limit 3 --json",
            interactive=True,
            hint="JSON output is great for automation and integration with Claude.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Next Steps",
            description=(
                "You now know the basics! Ready to dive deeper?\n\n"
                "Continue with:\n"
                "• [cyan]nexus learn medium[/] - Learn domain workflows\n"
                "• [cyan]nexus learn advanced[/] - Master batch operations\n\n"
                "Or explore on your own:\n"
                "• Try: nexus knowledge vault search [query]\n"
                "• Try: nexus teach course list\n"
                "• Try: nexus write manuscript list"
            ),
        )
    )

    return tutorial


# ─────────────────────────────────────────────────────────────────────────────
# Medium Tutorial
# ─────────────────────────────────────────────────────────────────────────────


def create_medium_tutorial() -> Tutorial:
    """Create the Medium-level tutorial."""
    tutorial = Tutorial(
        name="Domain Workflows",
        level=TutorialLevel.MEDIUM,
        description="Master research, teaching, and writing workflows with Nexus",
    )

    tutorial.add_step(
        TutorialStep(
            title="Research Workflow: Literature Discovery",
            description=(
                "Let's explore a research workflow: finding literature on a topic.\n\n"
                "Step 1: Search Zotero by topic\n"
                "Step 2: Get details on specific papers\n"
                "Step 3: Generate citations"
            ),
            command='nexus research zotero search "causal mediation" --limit 10',
            interactive=True,
            hint="Note the [key] for each paper - you'll need it for the next step.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Research Workflow: Paper Details",
            description=(
                "Now pick a paper key from your search results.\n"
                "Let's get the full details including abstract and metadata."
            ),
            command="nexus research zotero get [KEY]",
            interactive=True,
            hint="Replace [KEY] with an actual Zotero key from your results.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Research Workflow: Citations",
            description=(
                "Generate citations in different formats.\n"
                "This is useful for writing papers or creating bibliographies."
            ),
            command="nexus research zotero cite [KEY] --style bibtex",
            interactive=True,
            hint="Try --style apa for APA format. The key should be from your library.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Research Workflow: Exploring Tags",
            description=("Tags help organize your library.\nSee which tags you use most, then search by tag."),
            command="nexus research zotero tags --limit 20",
            interactive=True,
            hint="After seeing tags, try: nexus research zotero by-tag [TAG]",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Knowledge Workflow: Vault Search",
            description=(
                "Your Obsidian vault is full of notes.\nSearch across all notes using ripgrep for blazing-fast results."
            ),
            command='nexus knowledge vault search "regression"',
            interactive=True,
            hint="This searches all markdown files in your vault.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Knowledge Workflow: Reading Notes",
            description=("Once you find a note, read its full content.\nNexus parses frontmatter, tags, and links."),
            command="nexus knowledge vault read [NOTE_PATH]",
            interactive=True,
            hint="Use a path from your search results. Try --frontmatter to see just metadata.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Knowledge Workflow: Graph Analysis",
            description=("Your vault is a knowledge graph!\nSee statistics about connections and find central notes."),
            command="nexus knowledge vault graph --stats",
            interactive=True,
            hint="This shows most-connected notes. Try --json to export graph data.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Teaching Workflow: Course Overview",
            description=(
                "If you teach, Nexus tracks courses and materials.\nSee all your courses with status and progress."
            ),
            command="nexus teach course list",
            interactive=True,
            hint="Each course has a .STATUS file with metadata.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Writing Workflow: Manuscript Tracking",
            description=("Track all your manuscripts in one place.\nSee status, progress, and next actions."),
            command="nexus write manuscript list",
            interactive=True,
            hint="Active manuscripts show up first. Use --all to include archived.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Unified Search Across Everything",
            description=(
                "The ultimate power move: search EVERYTHING at once.\n"
                "Nexus searches Zotero, vault, and PDFs simultaneously."
            ),
            command='nexus knowledge search "bootstrap" --limit 15',
            interactive=True,
            hint="Narrow by source: --source zotero,vault (or just one)",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Medium Level Complete!",
            description=(
                "You now understand domain workflows!\n\n"
                "Key takeaways:\n"
                "• Research: zotero search → get → cite\n"
                "• Knowledge: vault search → read → graph\n"
                "• Teaching: course list → show → materials\n"
                "• Writing: manuscript list → show → stats\n\n"
                "Ready for advanced techniques?\n"
                "[cyan]nexus learn advanced[/]"
            ),
        )
    )

    return tutorial


# ─────────────────────────────────────────────────────────────────────────────
# Advanced Tutorial
# ─────────────────────────────────────────────────────────────────────────────


def create_advanced_tutorial() -> Tutorial:
    """Create the Advanced-level tutorial."""
    tutorial = Tutorial(
        name="Advanced Techniques",
        level=TutorialLevel.ADVANCED,
        description="Master batch operations, integrations, and power-user workflows",
    )

    tutorial.add_step(
        TutorialStep(
            title="Welcome to Advanced Nexus",
            description=(
                "This tutorial covers:\n"
                "• Batch operations on manuscripts\n"
                "• Graph exports for visualization\n"
                "• Integration patterns with Claude\n"
                "• JSON pipelines\n"
                "• Quarto automation\n\n"
                "These techniques are for power users who want to automate workflows."
            ),
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Batch Operations: Status Updates",
            description=(
                "Update status for multiple manuscripts at once.\nThis is faster than editing .STATUS files manually."
            ),
            command="nexus write manuscript batch-status paper1 paper2 --status under_review",
            interactive=True,
            hint="Replace paper1, paper2 with your actual manuscript names.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Batch Operations: Progress Tracking",
            description=("Update progress for multiple manuscripts in one command.\nFormat: manuscript:percentage"),
            command="nexus write manuscript batch-progress paper1:75 paper2:90",
            interactive=True,
            hint="This updates progress bars without opening files.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Batch Operations: Exporting Metadata",
            description=("Export all manuscript metadata to JSON or CSV.\nPerfect for analysis, reporting, or backup."),
            command="nexus write manuscript export manuscripts.json --format json",
            interactive=True,
            hint="Try --format csv for spreadsheet-friendly output.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Graph Visualization: Export Formats",
            description=(
                "Export your vault graph for visualization tools.\nSupported formats: GraphML (Gephi), D3.js, JSON"
            ),
            command="nexus knowledge vault export graphml graph.graphml --tags",
            interactive=True,
            hint="Open in Gephi, Cytoscape, or yEd for visual analysis.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Graph Visualization: D3 Export",
            description=(
                "D3.js format is perfect for web-based visualizations.\n"
                "Use with force-directed graphs or other D3 layouts."
            ),
            command="nexus knowledge vault export d3 graph-d3.json --limit 100",
            interactive=True,
            hint="--limit keeps the graph manageable for interactive visualizations.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Claude Integration: JSON Pipelines",
            description=(
                "Combine Nexus JSON output with Claude for analysis.\nExample workflow: Search → JSON → Claude analysis"
            ),
            command='nexus research zotero search "RCT" --json | head -20',
            interactive=True,
            hint="Pipe this to: claude -p 'Summarize these papers' (if you have claude CLI)",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Bibliography Management: Citation Checking",
            description=(
                "Check for missing or unused citations in manuscripts.\nPrevents citation errors before submission."
            ),
            command="nexus write bib check [MANUSCRIPT_NAME]",
            interactive=True,
            hint="This compares in-text citations with .bib file entries.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Quarto Automation: Project Building",
            description=("Build Quarto projects programmatically.\nUseful for batch rendering or CI/CD pipelines."),
            command="nexus teach quarto build [PATH] --format html",
            interactive=True,
            hint="Try --format pdf or --format revealjs for presentations.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Quarto Automation: Dependency Checking",
            description=("Check if all Quarto dependencies are available.\nPrevents build failures in advance."),
            command="nexus teach quarto info [PATH] --json",
            interactive=True,
            hint="JSON output includes version and dependency status.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Power User Patterns: Custom Workflows",
            description=(
                "Combine commands for custom workflows:\n\n"
                "1. Research Paper → Create Note:\n"
                "   nexus research zotero get [KEY] --json | ...\n\n"
                "2. Manuscript Status Report:\n"
                "   nexus write manuscript active --json > report.json\n\n"
                "3. Daily Literature Review:\n"
                "   nexus research zotero recent --limit 10"
            ),
            hint="Build shell aliases or scripts for your common patterns.",
        )
    )

    tutorial.add_step(
        TutorialStep(
            title="Advanced Complete - You're a Nexus Expert!",
            description=(
                "Congratulations! You've mastered:\n\n"
                "✓ Batch operations for efficiency\n"
                "✓ Graph exports for visualization\n"
                "✓ JSON pipelines for automation\n"
                "✓ Bibliography management\n"
                "✓ Quarto automation\n\n"
                "Next steps:\n"
                "• Create custom shell scripts\n"
                "• Integrate with Claude for AI workflows\n"
                "• Build your own automation patterns\n\n"
                "Check the docs: nexus --help\n"
                "Join discussions: github.com/Data-Wise/nexus-cli"
            ),
        )
    )

    return tutorial


# ─────────────────────────────────────────────────────────────────────────────
# Tutorial Registry
# ─────────────────────────────────────────────────────────────────────────────


def get_tutorial(level: TutorialLevel) -> Tutorial:
    """Get tutorial by level."""
    tutorials = {
        TutorialLevel.GETTING_STARTED: create_getting_started_tutorial,
        TutorialLevel.MEDIUM: create_medium_tutorial,
        TutorialLevel.ADVANCED: create_advanced_tutorial,
    }

    creator = tutorials.get(level)
    if not creator:
        raise ValueError(f"Unknown tutorial level: {level}")

    return creator()


def list_tutorials() -> None:
    """List all available tutorials."""
    console.print()
    console.print(
        Panel.fit(
            "[bold]Nexus Tutorials[/]\n\nLearn Nexus through interactive tutorials at different skill levels.",
            border_style="blue",
            title="🎓 Available Tutorials",
        )
    )
    console.print()

    table = Table(show_header=True, header_style="bold")
    table.add_column("Level", style="cyan", width=15)
    table.add_column("Name", style="white")
    table.add_column("Description")
    table.add_column("Steps", justify="right", style="dim")

    # Getting Started
    tutorial = create_getting_started_tutorial()
    table.add_row(
        "[green]Getting Started[/]",
        tutorial.name,
        tutorial.description[:60] + "...",
        str(len(tutorial.steps)),
    )

    # Medium
    tutorial = create_medium_tutorial()
    table.add_row("[yellow]Medium[/]", tutorial.name, tutorial.description[:60] + "...", str(len(tutorial.steps)))

    # Advanced
    tutorial = create_advanced_tutorial()
    table.add_row("[red]Advanced[/]", tutorial.name, tutorial.description[:60] + "...", str(len(tutorial.steps)))

    console.print(table)
    console.print()
    console.print("[dim]To start a tutorial:[/]")
    console.print("  [cyan]nexus learn getting-started[/]")
    console.print("  [cyan]nexus learn medium[/]")
    console.print("  [cyan]nexus learn advanced[/]")
    console.print()
