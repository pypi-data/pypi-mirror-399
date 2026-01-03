"""Manuscript management for Nexus CLI."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ManuscriptStatus:
    """Parsed .STATUS file for a manuscript."""

    status: str = "unknown"
    priority: str = "--"
    progress: int = 0
    next_action: str = ""
    manuscript_type: str = "research"
    target: str = ""

    @classmethod
    def from_file(cls, path: Path) -> "ManuscriptStatus":
        """Parse a .STATUS file."""
        if not path.exists():
            return cls()

        content = path.read_text()
        result = cls()

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("status:"):
                result.status = line.split(":", 1)[1].strip()
            elif line.startswith("priority:"):
                result.priority = line.split(":", 1)[1].strip()
            elif line.startswith("progress:"):
                try:
                    result.progress = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("next:"):
                result.next_action = line.split(":", 1)[1].strip()
            elif line.startswith("type:"):
                result.manuscript_type = line.split(":", 1)[1].strip()
            elif line.startswith("target:"):
                result.target = line.split(":", 1)[1].strip()

        return result


@dataclass
class QuartoManuscript:
    """Parsed _quarto.yml for manuscript projects."""

    title: str = ""
    authors: list[str] = field(default_factory=list)
    article_file: str = "index.qmd"
    format_type: str = "manuscript"

    @classmethod
    def from_file(cls, path: Path) -> Optional["QuartoManuscript"]:
        """Parse a _quarto.yml file."""
        if not path.exists():
            return None

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return None

        result = cls()

        # Get project type
        project = data.get("project", {})
        result.format_type = project.get("type", "default")

        # Get manuscript settings
        manuscript = data.get("manuscript", {})
        result.article_file = manuscript.get("article", "index.qmd")

        # Get title from various sources
        result.title = data.get("title", "")

        # Get authors
        authors = data.get("author", [])
        if isinstance(authors, list):
            for author in authors:
                if isinstance(author, dict):
                    name = author.get("name", "")
                    if name:
                        result.authors.append(name)
                elif isinstance(author, str):
                    result.authors.append(author)

        return result


@dataclass
class Manuscript:
    """A research manuscript."""

    name: str
    path: str
    title: str = ""
    status: str = "unknown"
    progress: int = 0
    target: str = ""
    next_action: str = ""
    authors: list[str] = field(default_factory=list)
    format_type: str = "unknown"  # quarto, latex, markdown
    main_file: str = ""
    word_count: int = 0
    last_modified: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "title": self.title or self.name,
            "status": self.status,
            "progress": self.progress,
            "target": self.target,
            "next_action": self.next_action,
            "authors": self.authors,
            "format_type": self.format_type,
            "main_file": self.main_file,
            "word_count": self.word_count,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
        }

    @property
    def status_emoji(self) -> str:
        """Get emoji for status."""
        status_lower = self.status.lower()
        if "complete" in status_lower or "published" in status_lower:
            return "✅"
        elif "review" in status_lower:
            return "📬"
        elif "revision" in status_lower:
            return "✏️"
        elif "draft" in status_lower:
            return "📝"
        elif "active" in status_lower:
            return "🔥"
        elif "paused" in status_lower or "hold" in status_lower:
            return "⏸️"
        elif "idea" in status_lower or "planning" in status_lower:
            return "💡"
        else:
            return "📄"


class ManuscriptManager:
    """Manage research manuscripts."""

    def __init__(self, manuscripts_dir: Path, templates_dir: Path | None = None):
        """Initialize manuscript manager.

        Args:
            manuscripts_dir: Path to manuscripts directory (e.g., ~/projects/research)
            templates_dir: Path to manuscript templates
        """
        self.manuscripts_dir = Path(manuscripts_dir).expanduser()
        self.templates_dir = Path(templates_dir).expanduser() if templates_dir else None

    def exists(self) -> bool:
        """Check if manuscripts directory exists."""
        return self.manuscripts_dir.exists()

    def list_manuscripts(self, include_archived: bool = False) -> list[Manuscript]:
        """List all manuscripts in the manuscripts directory."""
        if not self.exists():
            return []

        manuscripts = []
        for ms_path in sorted(self.manuscripts_dir.iterdir()):
            if not ms_path.is_dir():
                continue
            if ms_path.name.startswith("."):
                continue

            manuscript = self._load_manuscript(ms_path)
            if manuscript:
                # Filter archived if requested
                if not include_archived:
                    status_lower = manuscript.status.lower()
                    if "archive" in status_lower or "complete" in status_lower:
                        continue
                manuscripts.append(manuscript)

        # Sort by progress (in-progress first), then by name
        manuscripts.sort(
            key=lambda m: (
                0 if m.status.lower() in ("active", "draft", "revision") else 1,
                -m.progress,
                m.name.lower(),
            )
        )

        return manuscripts

    def get_manuscript(self, name: str) -> Manuscript | None:
        """Get a specific manuscript by name."""
        ms_path = self.manuscripts_dir / name
        if not ms_path.exists():
            # Try case-insensitive and partial match
            for p in self.manuscripts_dir.iterdir():
                if p.name.lower() == name.lower():
                    ms_path = p
                    break
                if name.lower() in p.name.lower():
                    ms_path = p
                    break
            else:
                return None

        return self._load_manuscript(ms_path)

    def _load_manuscript(self, ms_path: Path) -> Manuscript | None:
        """Load manuscript data from a directory."""
        if not ms_path.is_dir():
            return None

        # Parse .STATUS file
        status_file = ms_path / ".STATUS"
        status = ManuscriptStatus.from_file(status_file)

        # Determine format and get metadata
        format_type = "unknown"
        title = ""
        authors = []
        main_file = ""

        # Check for Quarto manuscript
        quarto_file = ms_path / "_quarto.yml"
        if quarto_file.exists():
            format_type = "quarto"
            quarto_config = QuartoManuscript.from_file(quarto_file)
            if quarto_config:
                title = quarto_config.title
                authors = quarto_config.authors
                main_file = quarto_config.article_file

                # Check _manuscript subfolder (Quarto manuscript format)
                manuscript_subfolder = ms_path / "_manuscript"
                if manuscript_subfolder.exists():
                    index_file = manuscript_subfolder / "index.qmd"
                    if index_file.exists():
                        main_file = str(index_file.relative_to(ms_path))

        # Check for LaTeX
        tex_files = list(ms_path.glob("*.tex"))
        if tex_files and format_type == "unknown":
            format_type = "latex"
            # Find main tex file (usually named main.tex or same as folder)
            for tf in tex_files:
                if tf.stem in ("main", ms_path.name, "manuscript"):
                    main_file = tf.name
                    break
            if not main_file and tex_files:
                main_file = tex_files[0].name

        # Check for plain markdown
        if format_type == "unknown":
            md_files = list(ms_path.glob("*.md"))
            if md_files:
                format_type = "markdown"
                for mf in md_files:
                    if mf.stem in ("manuscript", "main", "README"):
                        main_file = mf.name
                        break

        # Get last modified time
        last_modified = None
        try:
            stat = ms_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
        except Exception:
            pass

        # Estimate word count from main file
        word_count = 0
        if main_file:
            main_path = ms_path / main_file
            if main_path.exists():
                word_count = self._estimate_word_count(main_path)

        return Manuscript(
            name=ms_path.name,
            path=str(ms_path),
            title=title or self._title_from_name(ms_path.name),
            status=status.status,
            progress=status.progress,
            target=status.target,
            next_action=status.next_action,
            authors=authors,
            format_type=format_type,
            main_file=main_file,
            word_count=word_count,
            last_modified=last_modified,
        )

    def _title_from_name(self, name: str) -> str:
        """Generate a title from folder name."""
        # Convert folder name to title case
        return name.replace("-", " ").replace("_", " ").title()

    def _estimate_word_count(self, path: Path) -> int:
        """Estimate word count from a file."""
        try:
            content = path.read_text()
            # Remove YAML frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    content = content[end + 3 :]
            # Remove code blocks
            content = re.sub(r"```[\s\S]*?```", "", content)
            # Remove inline code
            content = re.sub(r"`[^`]+`", "", content)
            # Remove LaTeX math
            content = re.sub(r"\$\$[\s\S]*?\$\$", "", content)
            content = re.sub(r"\$[^$]+\$", "", content)
            # Count words
            words = content.split()
            return len(words)
        except Exception:
            return 0

    def get_by_status(self, status: str) -> list[Manuscript]:
        """Get manuscripts with a specific status."""
        all_manuscripts = self.list_manuscripts(include_archived=True)
        status_lower = status.lower()
        return [m for m in all_manuscripts if status_lower in m.status.lower()]

    def get_active(self) -> list[Manuscript]:
        """Get actively worked manuscripts."""
        all_manuscripts = self.list_manuscripts(include_archived=False)
        return [m for m in all_manuscripts if m.status.lower() in ("active", "draft", "revision", "under review")]

    def search(self, query: str) -> list[Manuscript]:
        """Search manuscripts by name or title."""
        all_manuscripts = self.list_manuscripts(include_archived=True)
        pattern = re.compile(query, re.IGNORECASE)
        return [m for m in all_manuscripts if pattern.search(m.name) or pattern.search(m.title)]

    def get_statistics(self) -> dict:
        """Get manuscript statistics."""
        all_manuscripts = self.list_manuscripts(include_archived=True)

        stats = {
            "total": len(all_manuscripts),
            "by_status": {},
            "by_format": {},
            "total_words": 0,
        }

        for m in all_manuscripts:
            # Count by status
            status = m.status.lower()
            if status not in stats["by_status"]:
                stats["by_status"][status] = 0
            stats["by_status"][status] += 1

            # Count by format
            fmt = m.format_type
            if fmt not in stats["by_format"]:
                stats["by_format"][fmt] = 0
            stats["by_format"][fmt] += 1

            # Total words
            stats["total_words"] += m.word_count

        return stats

    def get_deadlines(self) -> list[dict]:
        """Get manuscripts with deadlines/targets."""
        all_manuscripts = self.list_manuscripts(include_archived=False)
        deadlines = []

        for m in all_manuscripts:
            if m.target and m.status.lower() not in ("complete", "published", "archived"):
                deadlines.append(
                    {
                        "name": m.name,
                        "title": m.title,
                        "target": m.target,
                        "status": m.status,
                        "progress": m.progress,
                    }
                )

        return deadlines

    def batch_update_status(self, manuscripts: list[str], new_status: str) -> dict:
        """Update status for multiple manuscripts.

        Args:
            manuscripts: List of manuscript names
            new_status: New status to set

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "errors": []}

        for name in manuscripts:
            ms_path = self.manuscripts_dir / name
            status_file = ms_path / ".STATUS"

            if not ms_path.exists():
                results["failed"] += 1
                results["errors"].append(f"{name}: directory not found")
                continue

            try:
                # Read existing status or create new
                if status_file.exists():
                    content = status_file.read_text()
                    # Update status line
                    lines = content.split("\n")
                    updated = False
                    for i, line in enumerate(lines):
                        if line.startswith("status:"):
                            lines[i] = f"status: {new_status}"
                            updated = True
                            break
                    if not updated:
                        lines.insert(0, f"status: {new_status}")
                    status_file.write_text("\n".join(lines))
                else:
                    # Create new .STATUS file
                    status_file.write_text(f"status: {new_status}\nprogress: 0\n")

                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{name}: {str(e)}")

        return results

    def batch_update_progress(self, updates: dict[str, int]) -> dict:
        """Update progress for multiple manuscripts.

        Args:
            updates: Dictionary mapping manuscript names to progress values (0-100)

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "errors": []}

        for name, progress in updates.items():
            if not 0 <= progress <= 100:
                results["failed"] += 1
                results["errors"].append(f"{name}: invalid progress {progress} (must be 0-100)")
                continue

            ms_path = self.manuscripts_dir / name
            status_file = ms_path / ".STATUS"

            if not ms_path.exists():
                results["failed"] += 1
                results["errors"].append(f"{name}: directory not found")
                continue

            try:
                if status_file.exists():
                    content = status_file.read_text()
                    lines = content.split("\n")
                    updated = False
                    for i, line in enumerate(lines):
                        if line.startswith("progress:"):
                            lines[i] = f"progress: {progress}"
                            updated = True
                            break
                    if not updated:
                        lines.insert(1, f"progress: {progress}")
                    status_file.write_text("\n".join(lines))
                else:
                    status_file.write_text(f"progress: {progress}\n")

                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{name}: {str(e)}")

        return results

    def batch_archive(self, manuscripts: list[str]) -> dict:
        """Archive multiple manuscripts by moving to Archive subdirectory.

        Args:
            manuscripts: List of manuscript names to archive

        Returns:
            Dictionary with success/failure counts
        """
        results = {"success": 0, "failed": 0, "errors": [], "archived_to": []}

        archive_dir = self.manuscripts_dir / "Archive"
        archive_dir.mkdir(exist_ok=True)

        for name in manuscripts:
            ms_path = self.manuscripts_dir / name

            if not ms_path.exists():
                results["failed"] += 1
                results["errors"].append(f"{name}: directory not found")
                continue

            # Skip if already in Archive
            if ms_path.parent.name == "Archive":
                results["failed"] += 1
                results["errors"].append(f"{name}: already archived")
                continue

            try:
                dest_path = archive_dir / name

                # Check if destination exists
                if dest_path.exists():
                    results["failed"] += 1
                    results["errors"].append(f"{name}: already exists in Archive")
                    continue

                # Move to archive
                ms_path.rename(dest_path)

                # Update status
                status_file = dest_path / ".STATUS"
                if status_file.exists():
                    content = status_file.read_text()
                    lines = content.split("\n")
                    updated = False
                    for i, line in enumerate(lines):
                        if line.startswith("status:"):
                            lines[i] = "status: archived"
                            updated = True
                            break
                    if not updated:
                        lines.insert(0, "status: archived")
                    status_file.write_text("\n".join(lines))

                results["success"] += 1
                results["archived_to"].append(str(dest_path))
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{name}: {str(e)}")

        return results

    def batch_export_metadata(self, output_path: Path, format: str = "json") -> None:
        """Export metadata for all manuscripts to a file.

        Args:
            output_path: Path to save export file
            format: Export format (json or csv)
        """
        import json

        manuscripts = self.list_manuscripts(include_archived=False)

        if format == "json":
            data = [m.to_dict() for m in manuscripts]
            output_path.write_text(json.dumps(data, indent=2, default=str))
        elif format == "csv":
            import csv

            with open(output_path, "w", newline="") as f:
                if not manuscripts:
                    return

                writer = csv.DictWriter(
                    f,
                    fieldnames=["name", "title", "status", "progress", "target", "word_count", "path"],
                )
                writer.writeheader()

                for m in manuscripts:
                    writer.writerow(
                        {
                            "name": m.name,
                            "title": m.title,
                            "status": m.status,
                            "progress": m.progress,
                            "target": m.target or "",
                            "word_count": m.word_count,
                            "path": str(m.path),
                        }
                    )
        else:
            raise ValueError(f"Unsupported format: {format}")
