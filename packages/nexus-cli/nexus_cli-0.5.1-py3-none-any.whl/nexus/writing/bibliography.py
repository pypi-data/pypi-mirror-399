"""Bibliography management for Nexus CLI."""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BibEntry:
    """A bibliography entry."""

    key: str
    entry_type: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: str = ""
    journal: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "entry_type": self.entry_type,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
            "url": self.url,
            "abstract": self.abstract[:200] + "..." if len(self.abstract) > 200 else self.abstract,
        }

    def format_apa(self) -> str:
        """Format as APA citation."""
        if not self.authors:
            author_str = "Unknown"
        elif len(self.authors) == 1:
            author_str = self.authors[0]
        elif len(self.authors) == 2:
            author_str = f"{self.authors[0]} & {self.authors[1]}"
        elif len(self.authors) <= 5:
            author_str = ", ".join(self.authors[:-1]) + f", & {self.authors[-1]}"
        else:
            author_str = f"{self.authors[0]} et al."

        year = self.year or "n.d."
        return f"{author_str} ({year}). {self.title}."


class BibFileParser:
    """Parse BibTeX files."""

    def parse_file(self, path: Path) -> list[BibEntry]:
        """Parse a .bib file and return entries."""
        path = Path(path).expanduser()
        if not path.exists():
            return []

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return self._parse_bibtex(content)
        except Exception:
            return []

    def _parse_bibtex(self, content: str) -> list[BibEntry]:
        """Parse BibTeX content."""
        entries = []

        # Pattern for BibTeX entries
        entry_pattern = re.compile(r"@(\w+)\s*\{\s*([^,]+)\s*,(.+?)\n\s*\}", re.DOTALL | re.MULTILINE)

        for match in entry_pattern.finditer(content):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            fields_text = match.group(3)

            # Skip preamble, string, etc.
            if entry_type in ("preamble", "string", "comment"):
                continue

            # Parse fields
            fields = self._parse_fields(fields_text)

            entry = BibEntry(
                key=key,
                entry_type=entry_type,
                title=fields.get("title", ""),
                authors=self._parse_authors(fields.get("author", "")),
                year=fields.get("year", ""),
                journal=fields.get("journal", fields.get("booktitle", "")),
                doi=fields.get("doi", ""),
                url=fields.get("url", ""),
                abstract=fields.get("abstract", ""),
            )

            entries.append(entry)

        return entries

    def _parse_fields(self, text: str) -> dict:
        """Parse BibTeX fields from entry content."""
        fields = {}

        # Pattern for field = {value} or field = "value" or field = value
        field_pattern = re.compile(r"(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|\"([^\"]*)\"|(\d+))", re.DOTALL)

        for match in field_pattern.finditer(text):
            field_name = match.group(1).lower()
            value = match.group(2) or match.group(3) or match.group(4) or ""
            # Clean up value
            value = re.sub(r"\s+", " ", value.strip())
            value = value.replace("{", "").replace("}", "")
            fields[field_name] = value

        return fields

    def _parse_authors(self, author_str: str) -> list[str]:
        """Parse author string into list of names."""
        if not author_str:
            return []

        # Split by " and "
        authors = re.split(r"\s+and\s+", author_str, flags=re.IGNORECASE)

        # Clean up each name
        cleaned = []
        for author in authors:
            author = author.strip()
            # Handle "Last, First" format
            if "," in author:
                parts = author.split(",", 1)
                if len(parts) == 2:
                    author = f"{parts[1].strip()} {parts[0].strip()}"
            cleaned.append(author)

        return cleaned


class BibliographyManager:
    """Manage bibliographies for manuscripts."""

    def __init__(self, zotero_db: Path | None = None):
        """Initialize bibliography manager.

        Args:
            zotero_db: Path to Zotero database for integration
        """
        self.zotero_db = Path(zotero_db).expanduser() if zotero_db else None
        self._parser = BibFileParser()

    def parse_bib_file(self, path: Path) -> list[BibEntry]:
        """Parse a .bib file."""
        return self._parser.parse_file(path)

    def find_bib_files(self, manuscript_path: Path) -> list[Path]:
        """Find all .bib files in a manuscript directory."""
        manuscript_path = Path(manuscript_path).expanduser()
        if not manuscript_path.exists():
            return []

        bib_files = list(manuscript_path.rglob("*.bib"))
        return sorted(bib_files)

    def get_manuscript_bibliography(self, manuscript_path: Path) -> list[BibEntry]:
        """Get all bibliography entries for a manuscript."""
        bib_files = self.find_bib_files(manuscript_path)
        all_entries = []

        for bib_file in bib_files:
            entries = self.parse_bib_file(bib_file)
            all_entries.extend(entries)

        # Remove duplicates by key
        seen = set()
        unique = []
        for entry in all_entries:
            if entry.key not in seen:
                seen.add(entry.key)
                unique.append(entry)

        return unique

    def search_bibliography(
        self,
        manuscript_path: Path,
        query: str,
    ) -> list[BibEntry]:
        """Search bibliography entries for a manuscript."""
        entries = self.get_manuscript_bibliography(manuscript_path)
        pattern = re.compile(query, re.IGNORECASE)

        return [
            e
            for e in entries
            if (pattern.search(e.title) or pattern.search(e.key) or any(pattern.search(a) for a in e.authors))
        ]

    def get_from_zotero(self, key: str) -> BibEntry | None:
        """Get an entry from Zotero by key."""
        if not self.zotero_db or not self.zotero_db.exists():
            return None

        try:
            from nexus.research.zotero import ZoteroClient

            client = ZoteroClient(self.zotero_db)
            item = client.get(key)

            if not item:
                return None

            return BibEntry(
                key=item.key,
                entry_type=item.item_type,
                title=item.title,
                authors=item.authors,
                year=item.date[:4] if item.date else "",
                doi=item.doi,
                url=item.url,
                abstract=item.abstract,
            )
        except Exception:
            return None

    def search_zotero(self, query: str, limit: int = 20) -> list[BibEntry]:
        """Search Zotero library."""
        if not self.zotero_db or not self.zotero_db.exists():
            return []

        try:
            from nexus.research.zotero import ZoteroClient

            client = ZoteroClient(self.zotero_db)
            items = client.search(query, limit=limit)

            return [
                BibEntry(
                    key=item.key,
                    entry_type=item.item_type,
                    title=item.title,
                    authors=item.authors,
                    year=item.date[:4] if item.date else "",
                    doi=item.doi,
                    url=item.url,
                    abstract=item.abstract,
                )
                for item in items
            ]
        except Exception:
            return []

    def export_bibtex(self, entries: list[BibEntry]) -> str:
        """Export entries as BibTeX."""
        lines = []

        for entry in entries:
            # Build BibTeX entry
            lines.append(f"@{entry.entry_type}{{{entry.key},")
            lines.append(f"  title = {{{entry.title}}},")

            if entry.authors:
                author_str = " and ".join(entry.authors)
                lines.append(f"  author = {{{author_str}}},")

            if entry.year:
                lines.append(f"  year = {{{entry.year}}},")

            if entry.journal:
                lines.append(f"  journal = {{{entry.journal}}},")

            if entry.doi:
                lines.append(f"  doi = {{{entry.doi}}},")

            if entry.url:
                lines.append(f"  url = {{{entry.url}}},")

            lines.append("}")
            lines.append("")

        return "\n".join(lines)

    def find_cited_keys(self, content: str) -> list[str]:
        """Find citation keys used in content (LaTeX/Quarto format)."""
        keys = set()

        # LaTeX format: \cite{key1,key2} or \citep{key} or \citet{key}
        latex_pattern = re.compile(r"\\cite[pt]?\{([^}]+)\}")
        for match in latex_pattern.finditer(content):
            for key in match.group(1).split(","):
                keys.add(key.strip())

        # Pandoc/Quarto format: [@key1; @key2] or @key
        pandoc_pattern = re.compile(r"@([\w:-]+)")
        for match in pandoc_pattern.finditer(content):
            key = match.group(1)
            # Skip common false positives
            if key not in ("fig", "tbl", "eq", "sec", "lst"):
                keys.add(key)

        return sorted(keys)

    def check_citations(self, manuscript_path: Path) -> dict:
        """Check for missing or unused citations in a manuscript."""
        manuscript_path = Path(manuscript_path).expanduser()

        # Get all citation keys from bibliography
        bib_entries = self.get_manuscript_bibliography(manuscript_path)
        bib_keys = {e.key for e in bib_entries}

        # Get all cited keys from manuscript files
        cited_keys = set()
        for qmd_file in manuscript_path.rglob("*.qmd"):
            try:
                content = qmd_file.read_text()
                cited_keys.update(self.find_cited_keys(content))
            except Exception:
                pass

        for tex_file in manuscript_path.rglob("*.tex"):
            try:
                content = tex_file.read_text()
                cited_keys.update(self.find_cited_keys(content))
            except Exception:
                pass

        # Find missing and unused
        missing = cited_keys - bib_keys
        unused = bib_keys - cited_keys

        return {
            "cited_count": len(cited_keys),
            "bibliography_count": len(bib_keys),
            "missing": sorted(missing),
            "unused": sorted(unused),
            "all_good": len(missing) == 0,
        }
