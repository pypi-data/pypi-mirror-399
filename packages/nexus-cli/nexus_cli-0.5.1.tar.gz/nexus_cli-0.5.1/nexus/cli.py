"""
Nexus CLI - Knowledge workflow for research, teaching, and writing.

Claude is the brain, Nexus is the body.
"""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nexus import __version__
from nexus.utils.config import get_config

# Create the main app
app = typer.Typer(
    name="nexus",
    help="Knowledge workflow CLI for research, teaching, and writing",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# Domain subcommands
research_app = typer.Typer(help="[bold blue]🔬 Research[/] - Literature, Zotero, PDFs, simulations")
teach_app = typer.Typer(help="[bold green]📚 Teaching[/] - Courses, materials, Quarto")
write_app = typer.Typer(help="[bold yellow]✍️ Writing[/] - Manuscripts, bibliography, LaTeX")
knowledge_app = typer.Typer(help="[bold magenta]🧠 Knowledge[/] - Vault, search, connections")
integrate_app = typer.Typer(help="[bold cyan]🔌 Integrate[/] - aiterm, R, Git integrations")

# Register subcommands
app.add_typer(research_app, name="research")
app.add_typer(teach_app, name="teach")
app.add_typer(write_app, name="write")
app.add_typer(knowledge_app, name="knowledge")
app.add_typer(integrate_app, name="integrate")


# ─────────────────────────────────────────────────────────────────────────────
# Core Commands
# ─────────────────────────────────────────────────────────────────────────────


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(f"[bold]nexus[/] version [cyan]{__version__}[/]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    [bold]Nexus[/] - Knowledge workflow CLI for research, teaching, and writing.

    [dim]Claude is the brain, Nexus is the body.[/]
    """
    pass


@app.command()
def doctor() -> None:
    """Check Nexus health and integrations."""
    config = get_config()

    console.print(
        Panel.fit(
            "[bold]Nexus Health Check[/]",
            border_style="blue",
        )
    )

    table = Table(show_header=True, header_style="bold")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Path/Info", style="dim")

    # Check Zotero
    zotero_db = Path(config.zotero.database).expanduser()
    if zotero_db.exists():
        table.add_row("Zotero", "[green]✓ Found[/]", str(zotero_db))
    else:
        table.add_row("Zotero", "[red]✗ Not found[/]", str(zotero_db))

    # Check Vault
    vault_path = Path(config.vault.path).expanduser()
    if vault_path.exists():
        note_count = len(list(vault_path.rglob("*.md")))
        table.add_row("Vault", "[green]✓ Found[/]", f"{note_count} notes")
    else:
        table.add_row("Vault", "[red]✗ Not found[/]", str(vault_path))

    # Check PDF directories
    pdf_dirs = config.pdf.directories
    found_pdfs = 0
    for pdf_dir in pdf_dirs:
        path = Path(pdf_dir).expanduser()
        if path.exists():
            found_pdfs += len(list(path.rglob("*.pdf")))
    if found_pdfs > 0:
        table.add_row("PDFs", "[green]✓ Found[/]", f"{found_pdfs} files")
    else:
        table.add_row("PDFs", "[yellow]? No PDFs[/]", "Check config")

    # Check R
    import shutil

    r_path = shutil.which("R")
    if r_path:
        table.add_row("R", "[green]✓ Found[/]", r_path)
    else:
        table.add_row("R", "[yellow]○ Optional[/]", "Not in PATH")

    # Check ripgrep (for search)
    rg_path = shutil.which("rg")
    if rg_path:
        table.add_row("ripgrep", "[green]✓ Found[/]", rg_path)
    else:
        table.add_row("ripgrep", "[red]✗ Required[/]", "brew install ripgrep")

    # Check pdftotext (for PDF extraction)
    pdftotext_path = shutil.which("pdftotext")
    if pdftotext_path:
        table.add_row("pdftotext", "[green]✓ Found[/]", pdftotext_path)
    else:
        table.add_row("pdftotext", "[yellow]○ Optional[/]", "brew install poppler")

    # Check Quarto (for teaching)
    quarto_path = shutil.which("quarto")
    if quarto_path:
        table.add_row("Quarto", "[green]✓ Found[/]", quarto_path)
    else:
        table.add_row("Quarto", "[yellow]○ Optional[/]", "brew install quarto")

    # Check Teaching directory
    teaching_dir = Path(config.teaching.courses_dir).expanduser()
    if teaching_dir.exists():
        course_count = len([d for d in teaching_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
        table.add_row("Courses", "[green]✓ Found[/]", f"{course_count} courses")
    else:
        table.add_row("Courses", "[yellow]○ Not configured[/]", str(teaching_dir))

    console.print(table)
    console.print()

    # Summary
    console.print("[dim]Run[/] [cyan]nexus config[/] [dim]to view/edit configuration.[/]")


@app.command()
def config(
    key: Annotated[
        str | None,
        typer.Argument(help="Config key to view/set (e.g., 'vault.path')"),
    ] = None,
    value: Annotated[
        str | None,
        typer.Argument(help="Value to set"),
    ] = None,
    edit: Annotated[
        bool,
        typer.Option("--edit", "-e", help="Open config in editor"),
    ] = False,
) -> None:
    """View or edit Nexus configuration."""
    config_path = Path.home() / ".config" / "nexus" / "config.yaml"

    if edit:
        import os
        import subprocess

        editor = os.environ.get("EDITOR", "vim")
        subprocess.run([editor, str(config_path)])
        return

    if key is None:
        # Show full config
        console.print(
            Panel.fit(
                f"[bold]Configuration[/]\n[dim]{config_path}[/]",
                border_style="blue",
            )
        )

        cfg = get_config()

        table = Table(show_header=True, header_style="bold")
        table.add_column("Section", style="cyan")
        table.add_column("Key")
        table.add_column("Value", style="green")

        # Flatten config for display
        table.add_row("zotero", "database", str(cfg.zotero.database))
        table.add_row("zotero", "storage", str(cfg.zotero.storage))
        table.add_row("vault", "path", str(cfg.vault.path))
        table.add_row("vault", "templates", str(cfg.vault.templates))
        table.add_row("pdf", "directories", ", ".join(cfg.pdf.directories[:2]) + "...")
        table.add_row("teaching", "courses_dir", str(cfg.teaching.courses_dir))
        table.add_row("writing", "manuscripts_dir", str(cfg.writing.manuscripts_dir))
        table.add_row("output", "format", cfg.output.format)

        console.print(table)
        return

    if value is not None:
        # Set config value
        console.print(f"[yellow]Setting {key} = {value}[/]")
        console.print("[dim]Config update not yet implemented[/]")
        return

    # Get specific key
    cfg = get_config()
    parts = key.split(".")
    obj = cfg
    for part in parts:
        obj = getattr(obj, part, None)
        if obj is None:
            console.print(f"[red]Unknown config key: {key}[/]")
            raise typer.Exit(1)
    console.print(f"[cyan]{key}[/] = [green]{obj}[/]")


@app.command()
def learn(
    level: Annotated[
        str | None,
        typer.Argument(help="Tutorial level: getting-started, medium, advanced, or 'list' to show all"),
    ] = None,
    step: Annotated[
        int | None,
        typer.Option("--step", "-s", help="Start at specific step"),
    ] = None,
) -> None:
    """Interactive tutorials for learning Nexus.

    Examples:
        nexus learn                    # List all tutorials
        nexus learn list               # List all tutorials
        nexus learn getting-started    # Start beginner tutorial
        nexus learn medium             # Start intermediate tutorial
        nexus learn advanced           # Start advanced tutorial
        nexus learn medium --step 5    # Resume from step 5
    """
    from nexus.utils.tutorial import TutorialLevel, get_tutorial, list_tutorials

    # No argument or "list" shows all tutorials
    if level is None or level == "list":
        list_tutorials()
        return

    # Normalize level name
    level_normalized = level.lower().replace("_", "-")

    try:
        tutorial_level = TutorialLevel(level_normalized)
    except ValueError:
        console.print(f"[red]Error:[/] Unknown tutorial level: {level}")
        console.print("\n[dim]Available levels:[/]")
        console.print("  • getting-started")
        console.print("  • medium")
        console.print("  • advanced")
        console.print("\n[dim]Example:[/] nexus learn getting-started")
        raise typer.Exit(1)

    tutorial_obj = get_tutorial(tutorial_level)

    if step is not None:
        tutorial_obj.current_step = step - 1

    tutorial_obj.run()


# ─────────────────────────────────────────────────────────────────────────────
# Research Domain
# ─────────────────────────────────────────────────────────────────────────────


def _get_zotero_client():
    """Get configured ZoteroClient instance."""
    from nexus.research.zotero import ZoteroClient

    cfg = get_config()
    return ZoteroClient(
        db_path=Path(cfg.zotero.database).expanduser(),
        storage_path=Path(cfg.zotero.storage).expanduser(),
    )


def _get_pdf_extractor():
    """Get configured PDFExtractor instance."""
    from nexus.research.pdf import PDFExtractor

    cfg = get_config()
    return PDFExtractor(directories=[Path(d) for d in cfg.pdf.directories])


# Zotero subcommand
zotero_app = typer.Typer(help="Zotero library operations")
research_app.add_typer(zotero_app, name="zotero")


@zotero_app.command("search")
def zotero_search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 20,
    tag: Annotated[str | None, typer.Option("--tag", "-t", help="Filter by tag")] = None,
    item_type: Annotated[str | None, typer.Option("--type", help="Filter by type")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search Zotero library for papers."""
    import json

    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    results = client.search(query, limit=limit, tag=tag, item_type=item_type)

    if json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    if not results:
        console.print(f"[yellow]No results found for:[/] {query}")
        return

    console.print(f"[dim]Found {len(results)} results for:[/] [cyan]{query}[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Key", style="dim", width=10)
    table.add_column("Title", style="cyan")
    table.add_column("Authors")
    table.add_column("Year", width=6)

    for item in results:
        # Truncate title
        title = item.title[:50] + "..." if len(item.title) > 50 else item.title
        # Format authors
        if item.authors:
            if len(item.authors) > 2:
                authors = f"{item.authors[0]} et al."
            else:
                authors = ", ".join(item.authors)
        else:
            authors = ""
        authors = authors[:30] + "..." if len(authors) > 30 else authors
        # Get year
        year = item.date[:4] if item.date else ""

        table.add_row(item.key, title, authors, year)

    console.print(table)


@zotero_app.command("get")
def zotero_get(
    key: Annotated[str, typer.Argument(help="Zotero item key")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Get details for a specific Zotero item."""
    import json

    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    item = client.get(key)

    if not item:
        console.print(f"[red]Item not found:[/] {key}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(item.to_dict(), indent=2))
        return

    console.print(
        Panel(
            f"[bold]{item.title}[/]\n[dim]{item.key} • {item.item_type}[/]",
            border_style="blue",
        )
    )

    if item.authors:
        console.print(f"[dim]Authors:[/] {', '.join(item.authors)}")

    if item.date:
        console.print(f"[dim]Date:[/] {item.date}")

    if item.doi:
        console.print(f"[dim]DOI:[/] {item.doi}")

    if item.url:
        console.print(f"[dim]URL:[/] {item.url}")

    if item.tags:
        console.print(f"[dim]Tags:[/] {', '.join(item.tags)}")

    if item.collections:
        console.print(f"[dim]Collections:[/] {', '.join(item.collections)}")

    if item.abstract:
        console.print("\n[dim]─── Abstract ───[/]")
        console.print(item.abstract[:500] + "..." if len(item.abstract) > 500 else item.abstract)


@zotero_app.command("cite")
def zotero_cite(
    key: Annotated[str, typer.Argument(help="Zotero item key")],
    style: Annotated[str, typer.Option("--style", "-s", help="Citation style: apa, bibtex")] = "apa",
) -> None:
    """Generate citation for a Zotero item."""
    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    item = client.get(key)

    if not item:
        console.print(f"[red]Item not found:[/] {key}")
        raise typer.Exit(1)

    if style.lower() == "bibtex":
        console.print(item.citation_bibtex())
    else:
        console.print(item.citation_apa())


@zotero_app.command("recent")
def zotero_recent(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 10,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show recently modified Zotero items."""
    import json

    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    results = client.recent(limit=limit)

    if json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    console.print(f"[dim]Recent items (last {limit}):[/]\n")

    for i, item in enumerate(results, 1):
        year = item.date[:4] if item.date else "n.d."
        authors = item.authors[0].split()[-1] if item.authors else "Unknown"
        console.print(f"  {i}. [cyan]{authors} ({year})[/] {item.title[:60]}...")


@zotero_app.command("tags")
def zotero_tags(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max tags")] = 30,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List all tags with counts."""
    import json

    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    tags = client.tags(limit=limit)

    if json_output:
        print(json.dumps([{"tag": t[0], "count": t[1]} for t in tags], indent=2))
        return

    console.print(f"[dim]Top {len(tags)} tags:[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Tag", style="cyan")
    table.add_column("Count", justify="right")

    for tag, count in tags:
        table.add_row(tag, str(count))

    console.print(table)


@zotero_app.command("collections")
def zotero_collections(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List all collections with counts."""
    import json

    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    collections = client.collections()

    if json_output:
        print(json.dumps([{"name": c[0], "count": c[1]} for c in collections], indent=2))
        return

    console.print("[dim]Collections:[/]\n")

    for name, count in collections:
        console.print(f"  • [cyan]{name}[/] ({count} items)")


@zotero_app.command("by-tag")
def zotero_by_tag(
    tag: Annotated[str, typer.Argument(help="Tag to search for")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Get items with a specific tag."""
    import json

    client = _get_zotero_client()

    if not client.exists():
        console.print(f"[red]Zotero database not found:[/] {client.db_path}")
        raise typer.Exit(1)

    results = client.by_tag(tag, limit=limit)

    if json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    if not results:
        console.print(f"[yellow]No items found with tag:[/] {tag}")
        return

    console.print(f"[dim]Found {len(results)} items with tag:[/] [cyan]{tag}[/]\n")

    for i, item in enumerate(results, 1):
        year = item.date[:4] if item.date else "n.d."
        console.print(f"  {i}. [{item.key}] {item.title[:60]}... ({year})")


# PDF subcommand
pdf_app = typer.Typer(help="PDF operations")
research_app.add_typer(pdf_app, name="pdf")


@pdf_app.command("extract")
def pdf_extract(
    path: Annotated[Path, typer.Argument(help="Path to PDF file")],
    pages: Annotated[str | None, typer.Option("--pages", "-p", help="Page range (e.g., 1-5)")] = None,
    layout: Annotated[bool, typer.Option("--layout", "-l", help="Preserve layout")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Extract text from a PDF file."""
    import json

    extractor = _get_pdf_extractor()

    if not extractor.available():
        console.print("[red]pdftotext not installed[/]")
        console.print("[dim]Install with:[/] brew install poppler")
        raise typer.Exit(1)

    try:
        doc = extractor.extract(path, pages=pages, layout=layout)
    except FileNotFoundError:
        console.print(f"[red]PDF not found:[/] {path}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Extraction failed:[/] {e}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(doc.to_dict(), indent=2))
        return

    console.print(
        Panel(
            f"[bold]{doc.filename}[/]\n[dim]{doc.page_count} pages • {doc.size_bytes // 1024} KB[/]",
            border_style="blue",
        )
    )

    if pages:
        console.print(f"[dim]Pages:[/] {pages}\n")

    console.print(doc.text)


@pdf_app.command("search")
def pdf_search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search across all PDFs."""
    import json

    extractor = _get_pdf_extractor()

    results = extractor.search(query, limit=limit)

    if json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    if not results:
        console.print(f"[yellow]No PDFs found matching:[/] {query}")
        return

    console.print(f"[dim]Found {len(results)} PDFs matching:[/] [cyan]{query}[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("File", style="cyan")
    table.add_column("Context")

    for result in results:
        context = result.context[:60] + "..." if len(result.context) > 60 else result.context
        table.add_row(result.filename, context)

    console.print(table)


@pdf_app.command("list")
def pdf_list(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max files")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List PDFs in configured directories."""
    import json

    extractor = _get_pdf_extractor()

    pdfs = extractor.list_pdfs(limit=limit)

    if json_output:
        print(json.dumps(pdfs, indent=2))
        return

    # Show directory summary first
    summaries = extractor.summarize_directories()
    total = sum(s["count"] for s in summaries)

    console.print(f"[dim]PDF directories ({total} total files):[/]\n")

    for s in summaries:
        status = "[green]✓[/]" if s["exists"] else "[red]✗[/]"
        console.print(f"  {status} {s['directory']} ({s['count']} PDFs)")

    if pdfs:
        console.print(f"\n[dim]Recent PDFs (showing {len(pdfs)}):[/]\n")

        for pdf in pdfs[:limit]:
            size_kb = pdf["size_bytes"] // 1024
            console.print(f"  • [cyan]{pdf['filename']}[/] ({size_kb} KB)")


@pdf_app.command("info")
def pdf_info(
    path: Annotated[Path, typer.Argument(help="Path to PDF file")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show information about a PDF file."""
    import json

    extractor = _get_pdf_extractor()

    path = Path(path).expanduser()

    if not path.exists():
        console.print(f"[red]PDF not found:[/] {path}")
        raise typer.Exit(1)

    try:
        doc = extractor.extract(path, pages="1")
    except Exception as e:
        console.print(f"[red]Failed to read PDF:[/] {e}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(doc.to_dict(), indent=2))
        return

    console.print(
        Panel(
            f"[bold]{doc.filename}[/]",
            border_style="blue",
        )
    )

    console.print(f"[dim]Path:[/] {doc.path}")
    console.print(f"[dim]Pages:[/] {doc.page_count}")
    console.print(f"[dim]Size:[/] {doc.size_bytes // 1024} KB")

    if doc.title and doc.title != doc.filename:
        console.print(f"[dim]Title:[/] {doc.title}")

    console.print("\n[dim]─── First page preview ───[/]")
    preview = doc.text[:500] + "..." if len(doc.text) > 500 else doc.text
    console.print(preview)


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Domain
# ─────────────────────────────────────────────────────────────────────────────

vault_app = typer.Typer(help="Obsidian vault operations")
knowledge_app.add_typer(vault_app, name="vault")


def _get_vault_manager():
    """Get configured VaultManager instance."""
    from nexus.knowledge.vault import VaultManager

    cfg = get_config()
    return VaultManager(
        vault_path=Path(cfg.vault.path).expanduser(),
        templates_path=Path(cfg.vault.templates).expanduser(),
    )


@vault_app.command("search")
def vault_search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search vault notes using ripgrep."""
    import json

    vault = _get_vault_manager()

    if not vault.exists():
        console.print(f"[red]Vault not found:[/] {vault.vault_path}")
        console.print("[dim]Run[/] [cyan]nexus config vault.path[/] [dim]to check path[/]")
        raise typer.Exit(1)

    results = vault.search(query, limit=limit)

    if json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    if not results:
        console.print(f"[yellow]No results found for:[/] {query}")
        return

    console.print(f"[dim]Found {len(results)} results for:[/] [cyan]{query}[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Line", style="dim", justify="right")
    table.add_column("Content")

    for result in results:
        # Truncate content for display
        content = result.content[:80] + "..." if len(result.content) > 80 else result.content
        table.add_row(result.path, str(result.line_number), content)

    console.print(table)


@vault_app.command("read")
def vault_read(
    path: Annotated[str, typer.Argument(help="Note path (relative to vault)")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    frontmatter_only: Annotated[bool, typer.Option("--frontmatter", "-f", help="Show only frontmatter")] = False,
) -> None:
    """Read a note from the vault."""
    import json

    vault = _get_vault_manager()

    try:
        note = vault.read(path)
    except FileNotFoundError:
        console.print(f"[red]Note not found:[/] {path}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(note.to_dict(), indent=2))
        return

    if frontmatter_only:
        if note.frontmatter:
            import yaml

            console.print(
                Panel(
                    yaml.dump(note.frontmatter, default_flow_style=False),
                    title=f"[cyan]{note.title}[/] frontmatter",
                    border_style="dim",
                )
            )
        else:
            console.print("[dim]No frontmatter[/]")
        return

    # Show full note
    console.print(
        Panel(
            f"[bold]{note.title}[/]\n[dim]{note.path}[/]",
            border_style="blue",
        )
    )

    if note.frontmatter:
        import yaml

        console.print("[dim]─── Frontmatter ───[/]")
        console.print(yaml.dump(note.frontmatter, default_flow_style=False))

    if note.tags:
        console.print(f"[dim]Tags:[/] {', '.join(f'#{t}' for t in note.tags)}")

    if note.links:
        console.print(f"[dim]Links:[/] {', '.join(f'[[{l}]]' for l in note.links[:5])}")
        if len(note.links) > 5:
            console.print(f"[dim]  ... and {len(note.links) - 5} more[/]")

    console.print("\n[dim]─── Content ───[/]")
    console.print(note.content)


@vault_app.command("write")
def vault_write(
    path: Annotated[str, typer.Argument(help="Note path (relative to vault)")],
    content: Annotated[str | None, typer.Option("--content", "-c", help="Note content")] = None,
    stdin: Annotated[bool, typer.Option("--stdin", help="Read content from stdin")] = False,
    title: Annotated[str | None, typer.Option("--title", "-t", help="Note title for frontmatter")] = None,
) -> None:
    """Write content to a note in the vault."""
    import sys

    vault = _get_vault_manager()

    if stdin:
        content = sys.stdin.read()
    elif content is None:
        console.print("[red]Must provide --content or --stdin[/]")
        raise typer.Exit(1)

    # Build frontmatter
    frontmatter = {}
    if title:
        frontmatter["title"] = title
    frontmatter["created"] = __import__("datetime").date.today().isoformat()

    result_path = vault.write(path, content, frontmatter=frontmatter if frontmatter else None)
    console.print(f"[green]✓ Written:[/] {result_path}")


@vault_app.command("daily")
def vault_daily(
    open_note: Annotated[bool, typer.Option("--open", "-o", help="Open in default app")] = False,
) -> None:
    """Open or create today's daily note."""
    vault = _get_vault_manager()

    if not vault.exists():
        console.print(f"[red]Vault not found:[/] {vault.vault_path}")
        raise typer.Exit(1)

    daily_path = vault.daily()
    console.print(f"[green]✓ Daily note:[/] {daily_path}")

    if open_note:
        import subprocess

        subprocess.run(["open", str(daily_path)])


@vault_app.command("backlinks")
def vault_backlinks(
    path: Annotated[str, typer.Argument(help="Note path to find backlinks for")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Find notes that link to this note."""
    import json

    vault = _get_vault_manager()

    if not vault.exists():
        console.print(f"[red]Vault not found:[/] {vault.vault_path}")
        raise typer.Exit(1)

    backlinks = vault.backlinks(path)

    if json_output:
        print(json.dumps(backlinks, indent=2))
        return

    if not backlinks:
        console.print(f"[yellow]No backlinks found for:[/] {path}")
        return

    console.print(f"[dim]Found {len(backlinks)} notes linking to:[/] [cyan]{path}[/]\n")

    for link in backlinks:
        console.print(f"  • [cyan]{link}[/]")


@vault_app.command("recent")
def vault_recent(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 10,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show recently modified notes."""
    import json

    vault = _get_vault_manager()

    if not vault.exists():
        console.print(f"[red]Vault not found:[/] {vault.vault_path}")
        raise typer.Exit(1)

    recent = vault.recent(limit=limit)

    if json_output:
        print(json.dumps(recent, indent=2))
        return

    console.print(f"[dim]Recent notes (last {limit}):[/]\n")

    for i, path in enumerate(recent, 1):
        console.print(f"  {i}. [cyan]{path}[/]")


@vault_app.command("orphans")
def vault_orphans(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Find orphan notes (not linked from anywhere)."""
    import json

    vault = _get_vault_manager()

    if not vault.exists():
        console.print(f"[red]Vault not found:[/] {vault.vault_path}")
        raise typer.Exit(1)

    orphans = vault.orphans()

    if json_output:
        print(json.dumps(orphans, indent=2))
        return

    if not orphans:
        console.print("[green]✓ No orphan notes found[/]")
        return

    console.print(f"[yellow]Found {len(orphans)} orphan notes:[/]\n")

    for path in orphans[:20]:
        console.print(f"  • [dim]{path}[/]")

    if len(orphans) > 20:
        console.print(f"\n[dim]  ... and {len(orphans) - 20} more[/]")


@vault_app.command("template")
def vault_template(
    template_name: Annotated[str, typer.Argument(help="Template name")],
    dest: Annotated[str, typer.Option("--dest", "-d", help="Destination path")] = "",
    list_templates: Annotated[bool, typer.Option("--list", "-l", help="List available templates")] = False,
) -> None:
    """Create a note from a template."""
    vault = _get_vault_manager()

    if list_templates or not template_name:
        templates = vault.list_templates()
        if not templates:
            console.print("[yellow]No templates found[/]")
            console.print(f"[dim]Templates directory:[/] {vault.templates_path}")
            return

        console.print("[dim]Available templates:[/]\n")
        for t in templates:
            console.print(f"  • [cyan]{t}[/]")
        return

    if not dest:
        console.print("[red]Must provide --dest path[/]")
        raise typer.Exit(1)

    try:
        result_path = vault.template(template_name, dest)
        console.print(f"[green]✓ Created from template:[/] {result_path}")
    except FileNotFoundError:
        console.print(f"[red]Template not found:[/] {template_name}")
        console.print("[dim]Use[/] [cyan]nexus knowledge vault template --list[/] [dim]to see available templates[/]")
        raise typer.Exit(1)


@vault_app.command("graph")
def vault_graph(
    limit: Annotated[int | None, typer.Option("--limit", "-n", help="Limit nodes (keeps most connected)")] = None,
    include_tags: Annotated[bool, typer.Option("--tags", "-t", help="Include tag nodes")] = False,
    stats_only: Annotated[bool, typer.Option("--stats", "-s", help="Show statistics only")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Generate graph visualization data for the vault.

    Creates a graph representation showing notes and their connections (links).
    Optionally includes tags as nodes. Output can be used with graph visualization tools.
    """
    import json

    vault = _get_vault_manager()

    if stats_only:
        stats = vault.graph_stats()

        if json_output:
            print(json.dumps(stats, indent=2))
            return

        console.print("\n[bold cyan]Vault Graph Statistics[/]\n")

        console.print(f"  [dim]Total Notes:[/] {stats['total_notes']}")
        console.print(f"  [dim]Total Tags:[/] {stats['total_tags']}")
        console.print(f"  [dim]Total Connections:[/] {stats['total_connections']}")
        console.print(f"  [dim]Average Connections:[/] {stats['avg_connections']}")
        console.print(f"  [dim]Graph Density:[/] {stats['density']}")

        console.print("\n[dim]Most Connected Notes:[/]\n")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Note", style="cyan")
        table.add_column("Connections", justify="right", style="yellow")

        for note in stats["most_connected"][:10]:
            table.add_row(note["label"], str(note["connections"]))

        console.print(table)
        return

    # Generate full graph
    graph = vault.graph(limit=limit, include_tags=include_tags)

    if json_output:
        print(json.dumps(graph, indent=2, ensure_ascii=False))
        return

    console.print("\n[bold cyan]Vault Graph[/]\n")
    console.print(f"  [dim]Nodes:[/] {len(graph['nodes'])}")
    console.print(f"  [dim]Edges:[/] {len(graph['edges'])}")

    if include_tags:
        tag_nodes = [n for n in graph["nodes"] if n.get("type") == "tag"]
        console.print(f"  [dim]Tag Nodes:[/] {len(tag_nodes)}")

    console.print("\n[dim]Use[/] [cyan]--json[/] [dim]to export graph data for visualization tools[/]")


@vault_app.command("export")
def vault_export(
    format: Annotated[str, typer.Argument(help="Export format (graphml, d3, json)")],
    output: Annotated[Path, typer.Argument(help="Output file path")],
    limit: Annotated[int | None, typer.Option("--limit", "-n", help="Limit nodes (keeps most connected)")] = None,
    include_tags: Annotated[bool, typer.Option("--tags", "-t", help="Include tag nodes")] = False,
) -> None:
    """Export vault graph to various formats.

    Supported formats:
    - graphml: GraphML format (for Gephi, Cytoscape, yEd)
    - d3: D3.js-compatible JSON format
    - json: Raw JSON format (same as --json flag)

    Examples:
        nexus knowledge vault export graphml graph.graphml
        nexus knowledge vault export d3 graph-d3.json --tags
        nexus knowledge vault export json graph.json --limit 100
    """
    import json

    vault = _get_vault_manager()

    format_lower = format.lower()

    if format_lower == "graphml":
        vault.export_graphml(output, include_tags=include_tags, limit=limit)
        console.print(f"[green]✓[/] Exported GraphML to: [cyan]{output}[/]")
        console.print("[dim]Open with: Gephi, Cytoscape, yEd, or other graph tools[/]")

    elif format_lower == "d3":
        vault.export_d3(output, include_tags=include_tags, limit=limit)
        console.print(f"[green]✓[/] Exported D3.js format to: [cyan]{output}[/]")
        console.print("[dim]Use with D3.js force-directed graph or other D3 visualizations[/]")

    elif format_lower == "json":
        graph = vault.graph(limit=limit, include_tags=include_tags)
        output.write_text(json.dumps(graph, indent=2))
        console.print(f"[green]✓[/] Exported JSON to: [cyan]{output}[/]")
        console.print("[dim]Raw graph data format[/]")

    else:
        console.print(f"[red]Error:[/] Unknown format '{format}'")
        console.print("[dim]Supported formats: graphml, d3, json[/]")
        raise typer.Exit(1)

    # Show stats
    graph = vault.graph(limit=limit, include_tags=include_tags)
    console.print(f"\n[dim]Exported {len(graph['nodes'])} nodes and {len(graph['edges'])} edges[/]")


@knowledge_app.command("search")
def knowledge_search(
    query: Annotated[str, typer.Argument(help="Search query")],
    source: Annotated[
        str | None,
        typer.Option("--source", "-s", help="Limit to source: zotero, vault, pdf"),
    ] = None,
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 20,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Unified search across all knowledge sources."""
    import json

    from nexus.knowledge.search import UnifiedSearch

    cfg = get_config()

    searcher = UnifiedSearch(
        vault_path=Path(cfg.vault.path).expanduser(),
        zotero_db=Path(cfg.zotero.database).expanduser(),
        pdf_dirs=[Path(d).expanduser() for d in cfg.pdf.directories],
    )

    sources_list = source.split(",") if source else None
    results = searcher.search(query, sources=sources_list, limit=limit)

    if json_output:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return

    available = searcher.available_sources()
    if not available:
        console.print("[yellow]No knowledge sources available[/]")
        console.print("[dim]Run[/] [cyan]nexus doctor[/] [dim]to check configuration[/]")
        return

    if not results:
        console.print(f"[yellow]No results found for:[/] {query}")
        console.print(f"[dim]Searched:[/] {', '.join(sources_list or available)}")
        return

    console.print(f"[dim]Found {len(results)} results for:[/] [cyan]{query}[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Source", style="magenta", width=8)
    table.add_column("Title", style="cyan")
    table.add_column("Snippet")

    for result in results:
        snippet = result.snippet[:60] + "..." if len(result.snippet) > 60 else result.snippet
        table.add_row(result.source, result.title, snippet)

    console.print(table)


# ─────────────────────────────────────────────────────────────────────────────
# Teaching Domain
# ─────────────────────────────────────────────────────────────────────────────


def _get_course_manager():
    """Get configured CourseManager instance."""
    from nexus.teaching.courses import CourseManager

    cfg = get_config()
    return CourseManager(
        courses_dir=Path(cfg.teaching.courses_dir).expanduser(),
        materials_dir=Path(cfg.teaching.materials_dir).expanduser(),
    )


def _get_quarto_manager():
    """Get QuartoManager instance."""
    from nexus.teaching.quarto import QuartoManager

    return QuartoManager()


# Course subcommands
course_app = typer.Typer(help="Course management")
teach_app.add_typer(course_app, name="course")


@course_app.command("list")
def course_list(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List all courses."""
    import json

    manager = _get_course_manager()

    if not manager.exists():
        console.print(f"[red]Courses directory not found:[/] {manager.courses_dir}")
        raise typer.Exit(1)

    courses = manager.list_courses()

    if json_output:
        print(json.dumps([c.to_dict() for c in courses], indent=2))
        return

    if not courses:
        console.print("[yellow]No courses found[/]")
        console.print(f"[dim]Courses directory:[/] {manager.courses_dir}")
        return

    console.print(f"[dim]Found {len(courses)} courses:[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Course", style="cyan")
    table.add_column("Status")
    table.add_column("Progress", justify="right")
    table.add_column("Lectures", justify="right")
    table.add_column("Next Action")

    for course in courses:
        # Status color
        status_color = {
            "active": "green",
            "complete": "blue",
            "paused": "yellow",
            "archived": "dim",
        }.get(course.status.lower(), "white")

        progress_bar = "█" * (course.progress // 10) + "░" * (10 - course.progress // 10)

        table.add_row(
            course.name,
            f"[{status_color}]{course.status}[/]",
            f"{progress_bar} {course.progress}%",
            str(course.lecture_count),
            course.next_action[:40] + "..." if len(course.next_action) > 40 else course.next_action,
        )

    console.print(table)


@course_app.command("show")
def course_show(
    name: Annotated[str, typer.Argument(help="Course name (e.g., stat-440)")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show course details."""
    import json

    manager = _get_course_manager()
    course = manager.get_course(name)

    if not course:
        console.print(f"[red]Course not found:[/] {name}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(course.to_dict(), indent=2))
        return

    # Show course panel
    console.print(
        Panel(
            f"[bold]{course.title or course.name}[/]\n[dim]{course.path}[/]",
            border_style="blue",
        )
    )

    console.print(f"[dim]Status:[/] {course.status}")
    console.print(f"[dim]Progress:[/] {course.progress}%")

    if course.week:
        console.print(f"[dim]Current Week:[/] {course.week}")

    if course.formats:
        console.print(f"[dim]Formats:[/] {', '.join(course.formats)}")

    console.print(f"[dim]Lectures:[/] {course.lecture_count}")
    console.print(f"[dim]Assignments:[/] {course.assignment_count}")

    if course.next_action:
        console.print(f"\n[bold]Next:[/] {course.next_action}")


@course_app.command("lectures")
def course_lectures(
    name: Annotated[str, typer.Argument(help="Course name")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List lectures for a course."""
    import json

    manager = _get_course_manager()
    lectures = manager.list_lectures(name)

    if json_output:
        print(json.dumps([l.to_dict() for l in lectures], indent=2))
        return

    if not lectures:
        console.print(f"[yellow]No lectures found for:[/] {name}")
        return

    console.print(f"[dim]Lectures for {name}:[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Week", style="dim", width=6)
    table.add_column("Title", style="cyan")
    table.add_column("File")

    for lecture in lectures:
        week = str(lecture.week) if lecture.week else "-"
        table.add_row(week, lecture.title, lecture.name)

    console.print(table)


@course_app.command("materials")
def course_materials(
    name: Annotated[str, typer.Argument(help="Course name")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List all materials for a course."""
    import json

    manager = _get_course_manager()
    materials = manager.get_materials(name)

    if json_output:
        print(json.dumps(materials, indent=2))
        return

    if not materials:
        console.print(f"[yellow]No materials found for:[/] {name}")
        return

    # Group by type
    by_type: dict[str, list] = {}
    for mat in materials:
        mat_type = mat["type"]
        if mat_type not in by_type:
            by_type[mat_type] = []
        by_type[mat_type].append(mat)

    console.print(f"[dim]Materials for {name}:[/]\n")

    for mat_type, items in by_type.items():
        console.print(f"[bold]{mat_type.title()}[/] ({len(items)})")
        for item in items[:10]:
            console.print(f"  • [cyan]{item['name']}[/].{item['format']}")
        if len(items) > 10:
            console.print(f"  [dim]... and {len(items) - 10} more[/]")
        console.print()


@course_app.command("syllabus")
def course_syllabus(
    name: Annotated[str, typer.Argument(help="Course name")],
) -> None:
    """Show course syllabus."""
    manager = _get_course_manager()
    syllabus = manager.get_syllabus(name)

    if not syllabus:
        console.print(f"[yellow]No syllabus found for:[/] {name}")
        return

    console.print(
        Panel(
            f"[bold]Syllabus: {name}[/]",
            border_style="blue",
        )
    )
    console.print(syllabus)


# Quarto subcommands
quarto_app = typer.Typer(help="Quarto operations")
teach_app.add_typer(quarto_app, name="quarto")


@quarto_app.command("build")
def quarto_build(
    path: Annotated[Path, typer.Argument(help="Path to .qmd file or project directory")],
    format: Annotated[str | None, typer.Option("--format", "-f", help="Output format (html, pdf, revealjs)")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Build a Quarto document or project."""
    import json

    manager = _get_quarto_manager()

    if not manager.available():
        console.print("[red]Quarto not installed[/]")
        console.print("[dim]Install with:[/] brew install quarto")
        raise typer.Exit(1)

    console.print(f"[dim]Building:[/] {path}")
    if format:
        console.print(f"[dim]Format:[/] {format}")

    result = manager.render(path, output_format=format)

    if json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return

    if result.success:
        console.print(f"[green]✓ Build successful[/] ({result.duration_seconds:.1f}s)")
        if result.output_path:
            console.print(f"[dim]Output:[/] {result.output_path}")
    else:
        console.print("[red]✗ Build failed[/]")
        console.print(result.error)
        raise typer.Exit(1)


@quarto_app.command("preview")
def quarto_preview(
    path: Annotated[Path, typer.Argument(help="Path to .qmd file or project directory")],
    port: Annotated[int, typer.Option("--port", "-p", help="Preview server port")] = 4200,
) -> None:
    """Start Quarto preview server."""
    manager = _get_quarto_manager()

    if not manager.available():
        console.print("[red]Quarto not installed[/]")
        console.print("[dim]Install with:[/] brew install quarto")
        raise typer.Exit(1)

    console.print(f"[dim]Starting preview server for:[/] {path}")

    result = manager.preview(path, port=port)

    if result.get("success"):
        console.print("[green]✓ Preview server started[/]")
        console.print(f"[dim]URL:[/] [link={result['url']}]{result['url']}[/link]")
        console.print(f"[dim]PID:[/] {result['pid']}")
        console.print("\n[dim]Press Ctrl+C in the preview window to stop[/]")
    else:
        console.print("[red]✗ Failed to start preview[/]")
        console.print(result.get("error", "Unknown error"))
        raise typer.Exit(1)


@quarto_app.command("info")
def quarto_info(
    path: Annotated[Path | None, typer.Argument(help="Path to project")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show Quarto installation and project info."""
    import json

    manager = _get_quarto_manager()

    info = {
        "installed": manager.available(),
        "version": manager.version(),
    }

    if path:
        project = manager.load_project(path)
        if project:
            info["project"] = project.to_dict()
        deps = manager.check_dependencies(path)
        info["dependencies"] = deps

    if json_output:
        print(json.dumps(info, indent=2))
        return

    console.print(
        Panel.fit(
            "[bold]Quarto Info[/]",
            border_style="blue",
        )
    )

    if info["installed"]:
        console.print(f"[green]✓ Quarto installed[/] (version {info['version']})")
    else:
        console.print("[red]✗ Quarto not installed[/]")
        return

    if path and "project" in info:
        proj = info["project"]
        console.print(f"\n[bold]Project:[/] {proj['name']}")
        console.print(f"[dim]Type:[/] {proj['project_type']}")
        if proj["title"]:
            console.print(f"[dim]Title:[/] {proj['title']}")
        if proj["formats"]:
            console.print(f"[dim]Formats:[/] {', '.join(proj['formats'])}")

    if "dependencies" in info:
        console.print("\n[bold]Dependencies:[/]")
        for dep, available in info["dependencies"].items():
            if dep == "quarto_version":
                continue
            status = "[green]✓[/]" if available else "[red]✗[/]"
            console.print(f"  {status} {dep}")


@quarto_app.command("clean")
def quarto_clean(
    path: Annotated[Path, typer.Argument(help="Path to project directory")],
) -> None:
    """Clean Quarto build artifacts."""
    manager = _get_quarto_manager()

    result = manager.clean(path)

    if result["count"] > 0:
        console.print(f"[green]✓ Cleaned {result['count']} directories[/]")
        for cleaned in result["cleaned"]:
            console.print(f"  [dim]Removed:[/] {cleaned}")
    else:
        console.print("[dim]No build artifacts to clean[/]")


@quarto_app.command("formats")
def quarto_formats(
    path: Annotated[Path, typer.Argument(help="Path to project")],
) -> None:
    """List available output formats for a project."""
    manager = _get_quarto_manager()

    formats = manager.list_formats(path)

    if formats:
        console.print("[dim]Available formats:[/]\n")
        for fmt in formats:
            console.print(f"  • [cyan]{fmt}[/]")
    else:
        console.print("[dim]Default formats: html, pdf, docx[/]")


# ─────────────────────────────────────────────────────────────────────────────
# Writing Domain
# ─────────────────────────────────────────────────────────────────────────────


def _get_manuscript_manager():
    """Get configured ManuscriptManager instance."""
    from nexus.writing.manuscript import ManuscriptManager

    cfg = get_config()
    return ManuscriptManager(
        manuscripts_dir=Path(cfg.writing.manuscripts_dir).expanduser(),
        templates_dir=Path(cfg.writing.templates_dir).expanduser(),
    )


def _get_bibliography_manager():
    """Get configured BibliographyManager instance."""
    from nexus.writing.bibliography import BibliographyManager

    cfg = get_config()
    return BibliographyManager(
        zotero_db=Path(cfg.zotero.database).expanduser(),
    )


# Manuscript subcommands
manuscript_app = typer.Typer(help="Manuscript management")
write_app.add_typer(manuscript_app, name="manuscript")


@manuscript_app.command("list")
def manuscript_list(
    all_manuscripts: Annotated[bool, typer.Option("--all", "-a", help="Include archived/complete")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List all manuscripts."""
    import json

    manager = _get_manuscript_manager()

    if not manager.exists():
        console.print(f"[red]Manuscripts directory not found:[/] {manager.manuscripts_dir}")
        raise typer.Exit(1)

    manuscripts = manager.list_manuscripts(include_archived=all_manuscripts)

    if json_output:
        print(json.dumps([m.to_dict() for m in manuscripts], indent=2))
        return

    if not manuscripts:
        console.print("[yellow]No manuscripts found[/]")
        console.print(f"[dim]Manuscripts directory:[/] {manager.manuscripts_dir}")
        return

    console.print(f"[dim]Found {len(manuscripts)} manuscripts:[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("", width=2)  # Status emoji
    table.add_column("Manuscript", style="cyan")
    table.add_column("Status")
    table.add_column("Progress", justify="right")
    table.add_column("Target")

    for ms in manuscripts:
        # Status color
        status_color = {
            "active": "green",
            "draft": "yellow",
            "under review": "blue",
            "revision": "magenta",
            "complete": "dim",
            "published": "dim",
        }.get(ms.status.lower(), "white")

        progress_bar = "█" * (ms.progress // 10) + "░" * (10 - ms.progress // 10)

        table.add_row(
            ms.status_emoji,
            ms.name,
            f"[{status_color}]{ms.status}[/]",
            f"{progress_bar} {ms.progress}%",
            ms.target or "-",
        )

    console.print(table)


@manuscript_app.command("show")
def manuscript_show(
    name: Annotated[str, typer.Argument(help="Manuscript name")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show manuscript details."""
    import json

    manager = _get_manuscript_manager()
    manuscript = manager.get_manuscript(name)

    if not manuscript:
        console.print(f"[red]Manuscript not found:[/] {name}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps(manuscript.to_dict(), indent=2))
        return

    # Show manuscript panel
    console.print(
        Panel(
            f"[bold]{manuscript.title}[/]\n[dim]{manuscript.path}[/]",
            border_style="blue",
        )
    )

    console.print(f"[dim]Status:[/] {manuscript.status_emoji} {manuscript.status}")
    console.print(f"[dim]Progress:[/] {manuscript.progress}%")

    if manuscript.target:
        console.print(f"[dim]Target:[/] {manuscript.target}")

    if manuscript.authors:
        console.print(f"[dim]Authors:[/] {', '.join(manuscript.authors)}")

    console.print(f"[dim]Format:[/] {manuscript.format_type}")

    if manuscript.main_file:
        console.print(f"[dim]Main file:[/] {manuscript.main_file}")

    if manuscript.word_count > 0:
        console.print(f"[dim]Word count:[/] ~{manuscript.word_count:,}")

    if manuscript.last_modified:
        console.print(f"[dim]Last modified:[/] {manuscript.last_modified.strftime('%Y-%m-%d %H:%M')}")

    if manuscript.next_action:
        console.print(f"\n[bold]Next:[/] {manuscript.next_action}")


@manuscript_app.command("active")
def manuscript_active(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show actively worked manuscripts."""
    import json

    manager = _get_manuscript_manager()
    manuscripts = manager.get_active()

    if json_output:
        print(json.dumps([m.to_dict() for m in manuscripts], indent=2))
        return

    if not manuscripts:
        console.print("[dim]No active manuscripts[/]")
        return

    console.print(f"[dim]Active manuscripts ({len(manuscripts)}):[/]\n")

    for ms in manuscripts:
        progress_bar = "█" * (ms.progress // 10) + "░" * (10 - ms.progress // 10)
        console.print(f"  {ms.status_emoji} [cyan]{ms.name}[/] {progress_bar} {ms.progress}%")
        if ms.next_action:
            console.print(f"     [dim]Next:[/] {ms.next_action}")


@manuscript_app.command("search")
def manuscript_search(
    query: Annotated[str, typer.Argument(help="Search query")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search manuscripts by name or title."""
    import json

    manager = _get_manuscript_manager()
    results = manager.search(query)

    if json_output:
        print(json.dumps([m.to_dict() for m in results], indent=2))
        return

    if not results:
        console.print(f"[yellow]No manuscripts found matching:[/] {query}")
        return

    console.print(f"[dim]Found {len(results)} manuscripts matching:[/] [cyan]{query}[/]\n")

    for ms in results:
        console.print(f"  {ms.status_emoji} [cyan]{ms.name}[/] - {ms.status}")


@manuscript_app.command("stats")
def manuscript_stats(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show manuscript statistics."""
    import json

    manager = _get_manuscript_manager()
    stats = manager.get_statistics()

    if json_output:
        print(json.dumps(stats, indent=2))
        return

    console.print(
        Panel.fit(
            "[bold]Manuscript Statistics[/]",
            border_style="blue",
        )
    )

    console.print(f"[dim]Total manuscripts:[/] {stats['total']}")
    console.print(f"[dim]Total words:[/] ~{stats['total_words']:,}")

    if stats["by_status"]:
        console.print("\n[bold]By Status:[/]")
        for status, count in sorted(stats["by_status"].items(), key=lambda x: -x[1]):
            console.print(f"  • {status}: {count}")

    if stats["by_format"]:
        console.print("\n[bold]By Format:[/]")
        for fmt, count in sorted(stats["by_format"].items(), key=lambda x: -x[1]):
            console.print(f"  • {fmt}: {count}")


@manuscript_app.command("deadlines")
def manuscript_deadlines(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show manuscripts with targets/deadlines."""
    import json

    manager = _get_manuscript_manager()
    deadlines = manager.get_deadlines()

    if json_output:
        print(json.dumps(deadlines, indent=2))
        return

    if not deadlines:
        console.print("[dim]No manuscripts with targets[/]")
        return

    console.print("[dim]Manuscripts with targets:[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Manuscript", style="cyan")
    table.add_column("Target")
    table.add_column("Status")
    table.add_column("Progress", justify="right")

    for d in deadlines:
        table.add_row(d["name"], d["target"], d["status"], f"{d['progress']}%")

    console.print(table)


@manuscript_app.command("batch-status")
def manuscript_batch_status(
    manuscripts: Annotated[list[str], typer.Argument(help="Manuscript names (space-separated)")],
    status: Annotated[str, typer.Option("--status", "-s", help="New status")],
) -> None:
    """Update status for multiple manuscripts at once.

    Example:
        nexus write manuscript batch-status paper1 paper2 paper3 --status under_review
    """
    manager = _get_manuscript_manager()
    results = manager.batch_update_status(manuscripts, status)

    console.print(f"[green]✓[/] Updated {results['success']} manuscripts")

    if results["failed"] > 0:
        console.print(f"[yellow]![/] Failed: {results['failed']}")
        for error in results["errors"]:
            console.print(f"  [dim]{error}[/]")


@manuscript_app.command("batch-progress")
def manuscript_batch_progress(
    updates: Annotated[list[str], typer.Argument(help="Updates in format 'name:progress' (e.g., paper1:75 paper2:90)")],
) -> None:
    """Update progress for multiple manuscripts at once.

    Example:
        nexus write manuscript batch-progress paper1:75 paper2:90 paper3:50
    """
    # Parse updates
    parsed_updates = {}
    for update in updates:
        try:
            name, progress_str = update.split(":")
            progress = int(progress_str)
            parsed_updates[name] = progress
        except ValueError:
            console.print(f"[yellow]Warning:[/] Invalid format '{update}' (expected 'name:progress')")
            continue

    if not parsed_updates:
        console.print("[red]Error:[/] No valid updates provided")
        raise typer.Exit(1)

    manager = _get_manuscript_manager()
    results = manager.batch_update_progress(parsed_updates)

    console.print(f"[green]✓[/] Updated {results['success']} manuscripts")

    if results["failed"] > 0:
        console.print(f"[yellow]![/] Failed: {results['failed']}")
        for error in results["errors"]:
            console.print(f"  [dim]{error}[/]")


@manuscript_app.command("batch-archive")
def manuscript_batch_archive(
    manuscripts: Annotated[list[str], typer.Argument(help="Manuscript names to archive")],
) -> None:
    """Archive multiple manuscripts by moving them to Archive/ subdirectory.

    Example:
        nexus write manuscript batch-archive old-paper1 old-paper2 completed-paper
    """
    manager = _get_manuscript_manager()
    results = manager.batch_archive(manuscripts)

    console.print(f"[green]✓[/] Archived {results['success']} manuscripts")

    if results["archived_to"]:
        console.print("\n[dim]Archived to:[/]")
        for path in results["archived_to"]:
            console.print(f"  {path}")

    if results["failed"] > 0:
        console.print(f"\n[yellow]![/] Failed: {results['failed']}")
        for error in results["errors"]:
            console.print(f"  [dim]{error}[/]")


@manuscript_app.command("export")
def manuscript_export(
    output: Annotated[Path, typer.Argument(help="Output file path")],
    format: Annotated[str, typer.Option("--format", "-f", help="Export format (json, csv)")] = "json",
) -> None:
    """Export metadata for all manuscripts to a file.

    Examples:
        nexus write manuscript export manuscripts.json
        nexus write manuscript export manuscripts.csv --format csv
    """
    manager = _get_manuscript_manager()

    try:
        manager.batch_export_metadata(output, format=format)
        console.print(f"[green]✓[/] Exported manuscript metadata to: [cyan]{output}[/]")

        # Show count
        manuscripts = manager.list_manuscripts(include_archived=False)
        console.print(f"[dim]Exported {len(manuscripts)} manuscripts[/]")
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error exporting:[/] {e}")
        raise typer.Exit(1)


# Bibliography subcommands
bib_app = typer.Typer(help="Bibliography operations")
write_app.add_typer(bib_app, name="bib")


@bib_app.command("list")
def bib_list(
    manuscript: Annotated[str, typer.Argument(help="Manuscript name")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List bibliography entries for a manuscript."""
    import json

    ms_manager = _get_manuscript_manager()
    bib_manager = _get_bibliography_manager()

    manuscript_obj = ms_manager.get_manuscript(manuscript)
    if not manuscript_obj:
        console.print(f"[red]Manuscript not found:[/] {manuscript}")
        raise typer.Exit(1)

    entries = bib_manager.get_manuscript_bibliography(Path(manuscript_obj.path))

    if json_output:
        print(json.dumps([e.to_dict() for e in entries], indent=2))
        return

    if not entries:
        console.print(f"[yellow]No bibliography entries found for:[/] {manuscript}")
        return

    console.print(f"[dim]Found {len(entries)} entries for:[/] [cyan]{manuscript}[/]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Key", style="cyan", width=20)
    table.add_column("Authors", width=25)
    table.add_column("Year", width=6)
    table.add_column("Title")

    for entry in entries[:30]:
        authors = entry.authors[0] if entry.authors else ""
        if len(entry.authors) > 1:
            authors += " et al."
        title = entry.title[:40] + "..." if len(entry.title) > 40 else entry.title
        table.add_row(entry.key, authors, entry.year, title)

    console.print(table)

    if len(entries) > 30:
        console.print(f"\n[dim]... and {len(entries) - 30} more entries[/]")


@bib_app.command("search")
def bib_search(
    manuscript: Annotated[str, typer.Argument(help="Manuscript name")],
    query: Annotated[str, typer.Argument(help="Search query")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search bibliography entries."""
    import json

    ms_manager = _get_manuscript_manager()
    bib_manager = _get_bibliography_manager()

    manuscript_obj = ms_manager.get_manuscript(manuscript)
    if not manuscript_obj:
        console.print(f"[red]Manuscript not found:[/] {manuscript}")
        raise typer.Exit(1)

    entries = bib_manager.search_bibliography(Path(manuscript_obj.path), query)

    if json_output:
        print(json.dumps([e.to_dict() for e in entries], indent=2))
        return

    if not entries:
        console.print(f"[yellow]No entries found matching:[/] {query}")
        return

    console.print(f"[dim]Found {len(entries)} entries matching:[/] [cyan]{query}[/]\n")

    for entry in entries:
        console.print(f"[cyan]{entry.key}[/]")
        console.print(f"  {entry.format_apa()}")
        console.print()


@bib_app.command("check")
def bib_check(
    manuscript: Annotated[str, typer.Argument(help="Manuscript name")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Check for missing or unused citations."""
    import json

    ms_manager = _get_manuscript_manager()
    bib_manager = _get_bibliography_manager()

    manuscript_obj = ms_manager.get_manuscript(manuscript)
    if not manuscript_obj:
        console.print(f"[red]Manuscript not found:[/] {manuscript}")
        raise typer.Exit(1)

    result = bib_manager.check_citations(Path(manuscript_obj.path))

    if json_output:
        print(json.dumps(result, indent=2))
        return

    console.print(
        Panel.fit(
            f"[bold]Citation Check: {manuscript}[/]",
            border_style="blue",
        )
    )

    console.print(f"[dim]Citations in text:[/] {result['cited_count']}")
    console.print(f"[dim]Entries in bibliography:[/] {result['bibliography_count']}")

    if result["all_good"]:
        console.print("\n[green]✓ All citations have bibliography entries[/]")
    else:
        if result["missing"]:
            console.print(f"\n[red]Missing from bibliography ({len(result['missing'])}):[/]")
            for key in result["missing"][:10]:
                console.print(f"  • {key}")
            if len(result["missing"]) > 10:
                console.print(f"  [dim]... and {len(result['missing']) - 10} more[/]")

    if result["unused"]:
        console.print(f"\n[yellow]Unused entries ({len(result['unused'])}):[/]")
        for key in result["unused"][:10]:
            console.print(f"  • [dim]{key}[/]")
        if len(result["unused"]) > 10:
            console.print(f"  [dim]... and {len(result['unused']) - 10} more[/]")


@bib_app.command("zotero")
def bib_zotero(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 10,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Search Zotero for bibliography entries."""
    import json

    bib_manager = _get_bibliography_manager()
    entries = bib_manager.search_zotero(query, limit=limit)

    if json_output:
        print(json.dumps([e.to_dict() for e in entries], indent=2))
        return

    if not entries:
        console.print(f"[yellow]No Zotero entries found matching:[/] {query}")
        return

    console.print(f"[dim]Found {len(entries)} Zotero entries for:[/] [cyan]{query}[/]\n")

    for entry in entries:
        console.print(f"[cyan]{entry.key}[/]")
        console.print(f"  {entry.format_apa()}")
        if entry.doi:
            console.print(f"  [dim]DOI:[/] {entry.doi}")
        console.print()


# ─────────────────────────────────────────────────────────────────────────────
# Integration Commands (placeholder)
# ─────────────────────────────────────────────────────────────────────────────


@integrate_app.command("aiterm")
def integrate_aiterm(
    action: Annotated[str, typer.Argument(help="Action: install, status, remove")] = "status",
) -> None:
    """Manage aiterm integration."""
    console.print(f"[dim]aiterm integration:[/] [cyan]{action}[/]")
    console.print("[yellow]Not yet implemented - Phase 5[/]")


@integrate_app.command("claude")
def integrate_claude(
    action: Annotated[str, typer.Argument(help="Action: install, status, remove")] = "status",
) -> None:
    """Manage Claude Code plugin integration."""
    console.print(f"[dim]Claude Code plugin:[/] [cyan]{action}[/]")
    console.print("[yellow]Not yet implemented - Phase 5[/]")


if __name__ == "__main__":
    app()
