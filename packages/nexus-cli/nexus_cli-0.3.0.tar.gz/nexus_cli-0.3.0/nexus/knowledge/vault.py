"""Obsidian vault operations for Nexus CLI."""

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass
class SearchResult:
    """A search result from the vault."""

    path: str
    line_number: int
    content: str
    match_text: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "line_number": self.line_number,
            "content": self.content,
            "match_text": self.match_text,
        }


@dataclass
class Note:
    """A note from the vault."""

    path: str
    title: str
    content: str
    frontmatter: dict = field(default_factory=dict)
    links: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "title": self.title,
            "frontmatter": self.frontmatter,
            "links": self.links,
            "tags": self.tags,
            "content_preview": self.content[:200] + "..." if len(self.content) > 200 else self.content,
        }


class VaultManager:
    """Manages operations on an Obsidian vault."""

    def __init__(self, vault_path: Path, templates_path: Path | None = None):
        """Initialize with vault path.

        Args:
            vault_path: Path to the Obsidian vault root
            templates_path: Path to templates folder (defaults to vault/_SYSTEM/templates)
        """
        self.vault_path = Path(vault_path).expanduser()
        self.templates_path = (
            Path(templates_path).expanduser() if templates_path else self.vault_path / "_SYSTEM" / "templates"
        )

    def exists(self) -> bool:
        """Check if the vault exists."""
        return self.vault_path.exists() and self.vault_path.is_dir()

    def note_count(self) -> int:
        """Count total notes in vault."""
        if not self.exists():
            return 0
        return len(list(self.vault_path.rglob("*.md")))

    def _resolve_path(self, note_path: str) -> Path:
        """Resolve a note path to full path, adding .md if needed."""
        path = Path(note_path)
        if not path.suffix:
            path = path.with_suffix(".md")
        if not path.is_absolute():
            path = self.vault_path / path
        return path

    def read(self, note_path: str) -> Note:
        """Read a note from the vault.

        Args:
            note_path: Path relative to vault root (e.g., "projects/my-project.md")

        Returns:
            Note object with content and metadata

        Raises:
            FileNotFoundError: If note doesn't exist
        """
        full_path = self._resolve_path(note_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Note not found: {note_path}")

        content = full_path.read_text()

        # Parse frontmatter
        frontmatter = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml

                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    pass
                body = parts[2].strip()

        # Extract wiki links [[link]]
        links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)

        # Extract tags #tag
        tags = re.findall(r"(?:^|\s)#([a-zA-Z][a-zA-Z0-9_/-]*)", content)

        # Get title from frontmatter or filename
        title = frontmatter.get("title", full_path.stem)

        return Note(
            path=str(full_path.relative_to(self.vault_path)),
            title=title,
            content=body,
            frontmatter=frontmatter,
            links=links,
            tags=list(set(tags)),
        )

    def write(self, note_path: str, content: str, frontmatter: dict | None = None) -> Path:
        """Write content to a note.

        Args:
            note_path: Path relative to vault root
            content: Note content (markdown)
            frontmatter: Optional YAML frontmatter dict

        Returns:
            Full path to the created/updated note
        """
        full_path = self._resolve_path(note_path)

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Build content with frontmatter
        if frontmatter:
            import yaml

            fm_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            full_content = f"---\n{fm_str}---\n\n{content}"
        else:
            full_content = content

        full_path.write_text(full_content)
        return full_path

    def search(self, query: str, limit: int = 20) -> list[SearchResult]:
        """Search vault using ripgrep.

        Args:
            query: Search query (supports regex)
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not self.exists():
            return []

        try:
            result = subprocess.run(
                [
                    "rg",
                    "--json",
                    "--max-count",
                    str(limit * 2),  # Get extra to filter
                    "--glob",
                    "*.md",
                    "--ignore-case",
                    query,
                    str(self.vault_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError:
            # ripgrep not installed
            return self._fallback_search(query, limit)

        results = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("type") == "match":
                    match_data = data["data"]
                    path = Path(match_data["path"]["text"])
                    rel_path = str(path.relative_to(self.vault_path))

                    # Get line content
                    line_content = match_data["lines"]["text"].strip()

                    # Get match text
                    match_text = ""
                    if match_data.get("submatches"):
                        match_text = match_data["submatches"][0]["match"]["text"]

                    results.append(
                        SearchResult(
                            path=rel_path,
                            line_number=match_data["line_number"],
                            content=line_content,
                            match_text=match_text,
                        )
                    )

                    if len(results) >= limit:
                        break
            except (json.JSONDecodeError, KeyError):
                continue

        return results

    def _fallback_search(self, query: str, limit: int) -> list[SearchResult]:
        """Fallback search without ripgrep (slower)."""
        results = []
        pattern = re.compile(query, re.IGNORECASE)

        for md_file in self.vault_path.rglob("*.md"):
            try:
                content = md_file.read_text()
                for i, line in enumerate(content.split("\n"), 1):
                    if pattern.search(line):
                        results.append(
                            SearchResult(
                                path=str(md_file.relative_to(self.vault_path)),
                                line_number=i,
                                content=line.strip(),
                                match_text=query,
                            )
                        )
                        if len(results) >= limit:
                            return results
            except (OSError, UnicodeDecodeError):
                continue

        return results

    def search_files(self, query: str, limit: int = 20) -> list[str]:
        """Search for file names matching query.

        Args:
            query: Search query for file names

        Returns:
            List of matching file paths
        """
        if not self.exists():
            return []

        pattern = re.compile(query, re.IGNORECASE)
        matches = []

        for md_file in self.vault_path.rglob("*.md"):
            if pattern.search(md_file.name) or pattern.search(str(md_file)):
                matches.append(str(md_file.relative_to(self.vault_path)))
                if len(matches) >= limit:
                    break

        return matches

    def backlinks(self, note_path: str) -> list[str]:
        """Find notes that link to this note.

        Args:
            note_path: Path to note to find backlinks for

        Returns:
            List of paths to notes that link to this note
        """
        # Get the note name without extension for wiki link matching
        note_name = Path(note_path).stem

        # Search for [[note_name]] or [[note_name|alias]]
        pattern = rf"\[\[{re.escape(note_name)}(?:\|[^\]]+)?\]\]"

        results = self.search(pattern, limit=100)

        # Get unique file paths (excluding the source note)
        source_path = self._resolve_path(note_path)
        linking_notes = set()

        for result in results:
            full_result_path = self.vault_path / result.path
            if full_result_path != source_path:
                linking_notes.add(result.path)

        return sorted(linking_notes)

    def daily(self, target_date: date | None = None) -> Path:
        """Get or create a daily note.

        Args:
            target_date: Date for the note (defaults to today)

        Returns:
            Path to the daily note
        """
        if target_date is None:
            target_date = date.today()

        daily_path = f"50-DAILY/{target_date.isoformat()}.md"
        full_path = self._resolve_path(daily_path)

        if not full_path.exists():
            # Create from template or default
            template_content = self._load_template("daily")
            if template_content:
                content = template_content.replace("{{date}}", target_date.isoformat())
                content = content.replace("{{date:YYYY-MM-DD}}", target_date.isoformat())
                content = content.replace(
                    "{{date:dddd}}",
                    target_date.strftime("%A"),
                )
            else:
                content = f"# {target_date.isoformat()}\n\n## Tasks\n\n- [ ] \n\n## Notes\n\n"

            self.write(
                daily_path,
                content,
                frontmatter={"type": "daily", "date": target_date.isoformat()},
            )

        return full_path

    def _load_template(self, template_name: str) -> str | None:
        """Load a template by name.

        Args:
            template_name: Template name (without .md extension)

        Returns:
            Template content or None if not found
        """
        template_path = self.templates_path / f"{template_name}.md"

        if not template_path.exists():
            # Try alternate locations
            alt_paths = [
                self.templates_path / f"tpl-{template_name}.md",
                self.vault_path / "templates" / f"{template_name}.md",
                self.vault_path / "_templates" / f"{template_name}.md",
            ]
            for alt in alt_paths:
                if alt.exists():
                    template_path = alt
                    break
            else:
                return None

        return template_path.read_text()

    def template(
        self,
        template_name: str,
        dest_path: str,
        variables: dict | None = None,
    ) -> Path:
        """Create a note from a template.

        Args:
            template_name: Name of template to use
            dest_path: Destination path for new note
            variables: Variables to substitute in template

        Returns:
            Path to created note

        Raises:
            FileNotFoundError: If template doesn't exist
        """
        template_content = self._load_template(template_name)
        if template_content is None:
            raise FileNotFoundError(f"Template not found: {template_name}")

        # Substitute variables
        content = template_content
        if variables:
            for key, value in variables.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))

        # Always substitute date
        today = date.today()
        content = content.replace("{{date}}", today.isoformat())
        content = content.replace("{{date:YYYY-MM-DD}}", today.isoformat())

        # Write the note
        return self.write(dest_path, content)

    def list_templates(self) -> list[str]:
        """List available templates.

        Returns:
            List of template names
        """
        if not self.templates_path.exists():
            return []

        templates = []
        for md_file in self.templates_path.glob("*.md"):
            name = md_file.stem
            # Remove common prefixes
            if name.startswith("tpl-"):
                name = name[4:]
            templates.append(name)

        return sorted(templates)

    def recent(self, limit: int = 10) -> list[str]:
        """Get recently modified notes.

        Args:
            limit: Maximum number of notes to return

        Returns:
            List of note paths, most recent first
        """
        if not self.exists():
            return []

        notes = []
        for md_file in self.vault_path.rglob("*.md"):
            # Skip system folders
            rel_path = md_file.relative_to(self.vault_path)
            if str(rel_path).startswith(("_", ".")):
                continue
            notes.append((md_file, md_file.stat().st_mtime))

        # Sort by modification time, most recent first
        notes.sort(key=lambda x: x[1], reverse=True)

        return [str(n[0].relative_to(self.vault_path)) for n in notes[:limit]]

    def orphans(self) -> list[str]:
        """Find orphan notes (not linked from anywhere).

        Returns:
            List of paths to orphan notes
        """
        if not self.exists():
            return []

        # Get all notes
        all_notes = set()
        for md_file in self.vault_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.vault_path)
            if not str(rel_path).startswith(("_", ".")):
                all_notes.add(md_file.stem)

        # Find all links
        linked_notes = set()
        for md_file in self.vault_path.rglob("*.md"):
            try:
                content = md_file.read_text()
                links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)
                linked_notes.update(links)
            except (OSError, UnicodeDecodeError):
                continue

        # Find orphans
        orphans = all_notes - linked_notes

        # Get full paths
        orphan_paths = []
        for md_file in self.vault_path.rglob("*.md"):
            if md_file.stem in orphans:
                rel_path = md_file.relative_to(self.vault_path)
                if not str(rel_path).startswith(("_", ".")):
                    orphan_paths.append(str(rel_path))

        return sorted(orphan_paths)

    def graph(self, limit: int | None = None, include_tags: bool = False) -> dict:
        """Generate graph data for vault visualization.

        Creates a graph representation of notes and their connections.

        Args:
            limit: Optional limit on number of nodes (takes most connected)
            include_tags: Include tag nodes in the graph

        Returns:
            Graph dict with 'nodes' and 'edges' lists
        """
        if not self.exists():
            return {"nodes": [], "edges": []}

        # Collect all notes and their links
        note_data = {}
        tag_connections = {}

        for md_file in self.vault_path.rglob("*.md"):
            rel_path = md_file.relative_to(self.vault_path)
            if str(rel_path).startswith(("_", ".")):
                continue

            try:
                content = md_file.read_text()
                note_id = md_file.stem

                # Extract links
                links = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content)

                # Extract tags if requested
                tags = []
                if include_tags:
                    tags = re.findall(r"#([\w/-]+)", content)
                    for tag in tags:
                        if tag not in tag_connections:
                            tag_connections[tag] = []
                        tag_connections[tag].append(note_id)

                note_data[note_id] = {
                    "path": str(rel_path),
                    "links": links,
                    "tags": tags,
                    "size": len(content),
                }
            except (OSError, UnicodeDecodeError):
                continue

        # Calculate connectivity scores
        link_counts = {}
        for note_id, data in note_data.items():
            # Count outgoing links
            out_links = len(data["links"])
            # Count incoming links (how many notes link to this one)
            in_links = sum(1 for other_data in note_data.values() if note_id in other_data["links"])
            link_counts[note_id] = out_links + in_links

        # Apply limit by taking most connected nodes
        if limit and len(note_data) > limit:
            sorted_notes = sorted(link_counts.items(), key=lambda x: x[1], reverse=True)
            keep_notes = {note_id for note_id, _ in sorted_notes[:limit]}
            note_data = {k: v for k, v in note_data.items() if k in keep_notes}

        # Build nodes list
        nodes = []
        for note_id, data in note_data.items():
            nodes.append(
                {
                    "id": note_id,
                    "label": note_id.replace("-", " ").replace("_", " ").title(),
                    "path": data["path"],
                    "size": min(data["size"] / 100, 50),  # Scale size for visualization
                    "connections": link_counts.get(note_id, 0),
                    "tags": data["tags"],
                }
            )

        # Add tag nodes if requested
        if include_tags:
            for tag, connected_notes in tag_connections.items():
                # Only include tags with multiple connections
                if len(connected_notes) > 1:
                    nodes.append(
                        {
                            "id": f"tag:{tag}",
                            "label": f"#{tag}",
                            "type": "tag",
                            "connections": len(connected_notes),
                        }
                    )

        # Build edges list
        edges = []
        edge_id = 0
        for note_id, data in note_data.items():
            for target in data["links"]:
                # Only include edge if target exists in our node set
                if target in note_data:
                    edges.append(
                        {
                            "id": edge_id,
                            "source": note_id,
                            "target": target,
                            "type": "link",
                        }
                    )
                    edge_id += 1

            # Add tag edges if requested
            if include_tags:
                for tag in data["tags"]:
                    if f"tag:{tag}" in [n["id"] for n in nodes]:
                        edges.append(
                            {
                                "id": edge_id,
                                "source": note_id,
                                "target": f"tag:{tag}",
                                "type": "tag",
                            }
                        )
                        edge_id += 1

        return {"nodes": nodes, "edges": edges}

    def graph_stats(self) -> dict:
        """Get statistics about the vault graph.

        Returns:
            Dictionary with graph metrics
        """
        graph_data = self.graph()
        nodes = graph_data["nodes"]
        edges = graph_data["edges"]

        if not nodes:
            return {
                "total_notes": 0,
                "total_connections": 0,
                "avg_connections": 0,
                "most_connected": [],
                "clusters": 0,
            }

        # Calculate statistics
        connection_counts = [n["connections"] for n in nodes if "connections" in n]
        avg_connections = sum(connection_counts) / len(connection_counts) if connection_counts else 0

        # Find most connected notes
        sorted_nodes = sorted(nodes, key=lambda x: x.get("connections", 0), reverse=True)
        most_connected = [
            {
                "id": n["id"],
                "label": n["label"],
                "connections": n.get("connections", 0),
            }
            for n in sorted_nodes[:10]
        ]

        return {
            "total_notes": len([n for n in nodes if n.get("type") != "tag"]),
            "total_tags": len([n for n in nodes if n.get("type") == "tag"]),
            "total_connections": len(edges),
            "avg_connections": round(avg_connections, 2),
            "most_connected": most_connected,
            "density": round(len(edges) / (len(nodes) * (len(nodes) - 1)) * 2, 4) if len(nodes) > 1 else 0,
        }
