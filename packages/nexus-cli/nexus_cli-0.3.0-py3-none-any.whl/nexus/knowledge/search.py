"""Unified search across all knowledge sources."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from nexus.knowledge.vault import VaultManager


class SearchSource(str, Enum):
    """Available search sources."""

    VAULT = "vault"
    ZOTERO = "zotero"
    PDF = "pdf"
    ALL = "all"


@dataclass
class UnifiedSearchResult:
    """A unified search result from any source."""

    source: str
    path: str
    title: str
    snippet: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "path": self.path,
            "title": self.title,
            "snippet": self.snippet,
            "score": self.score,
            "metadata": self.metadata,
        }


class UnifiedSearch:
    """Unified search across all knowledge sources."""

    def __init__(
        self,
        vault_path: Path | None = None,
        zotero_db: Path | None = None,
        pdf_dirs: list[Path] | None = None,
    ):
        """Initialize search with available sources.

        Args:
            vault_path: Path to Obsidian vault
            zotero_db: Path to Zotero SQLite database
            pdf_dirs: List of directories containing PDFs
        """
        self.vault_path = Path(vault_path).expanduser() if vault_path else None
        self.zotero_db = Path(zotero_db).expanduser() if zotero_db else None
        self.pdf_dirs = [Path(d).expanduser() for d in pdf_dirs] if pdf_dirs else []

        # Initialize managers
        self._vault_manager: VaultManager | None = None
        if self.vault_path and self.vault_path.exists():
            self._vault_manager = VaultManager(self.vault_path)

    @property
    def vault(self) -> VaultManager | None:
        """Get vault manager."""
        return self._vault_manager

    def available_sources(self) -> list[str]:
        """Get list of available search sources."""
        sources = []

        if self._vault_manager and self._vault_manager.exists():
            sources.append("vault")

        if self.zotero_db and self.zotero_db.exists():
            sources.append("zotero")

        for pdf_dir in self.pdf_dirs:
            if pdf_dir.exists():
                sources.append("pdf")
                break

        return sources

    def search(
        self,
        query: str,
        sources: list[str] | None = None,
        limit: int = 20,
    ) -> list[UnifiedSearchResult]:
        """Search across specified sources.

        Args:
            query: Search query
            sources: List of sources to search (default: all available)
            limit: Maximum results per source

        Returns:
            List of unified search results
        """
        if sources is None:
            sources = self.available_sources()

        results: list[UnifiedSearchResult] = []

        # Search each source
        for source in sources:
            if source == "vault":
                results.extend(self._search_vault(query, limit))
            elif source == "zotero":
                results.extend(self._search_zotero(query, limit))
            elif source == "pdf":
                results.extend(self._search_pdfs(query, limit))

        # Sort by score (higher first)
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    def _search_vault(self, query: str, limit: int) -> list[UnifiedSearchResult]:
        """Search vault notes."""
        if not self._vault_manager:
            return []

        vault_results = self._vault_manager.search(query, limit=limit)
        results = []

        for vr in vault_results:
            # Calculate simple relevance score
            score = 1.0
            if vr.match_text.lower() == query.lower():
                score = 2.0  # Exact match bonus

            results.append(
                UnifiedSearchResult(
                    source="vault",
                    path=vr.path,
                    title=Path(vr.path).stem.replace("-", " ").replace("_", " ").title(),
                    snippet=vr.content[:150] + "..." if len(vr.content) > 150 else vr.content,
                    score=score,
                    metadata={
                        "line_number": vr.line_number,
                        "match_text": vr.match_text,
                    },
                )
            )

        return results

    def _search_zotero(self, query: str, limit: int) -> list[UnifiedSearchResult]:
        """Search Zotero library."""
        if not self.zotero_db or not self.zotero_db.exists():
            return []

        try:
            from nexus.research.zotero import ZoteroClient

            client = ZoteroClient(self.zotero_db)
            items = client.search(query, limit=limit)
            results = []

            for item in items:
                # Build author string
                if item.authors:
                    if len(item.authors) > 2:
                        author_str = f"{item.authors[0]} et al."
                    else:
                        author_str = ", ".join(item.authors)
                else:
                    author_str = "Unknown"

                year = item.date[:4] if item.date else "n.d."

                # Calculate score
                score = 1.5  # Base score for Zotero (slightly higher than vault)
                if query.lower() in item.title.lower():
                    score = 2.5  # Title match bonus

                results.append(
                    UnifiedSearchResult(
                        source="zotero",
                        path=item.key,
                        title=item.title,
                        snippet=f"{author_str} ({year})",
                        score=score,
                        metadata={
                            "key": item.key,
                            "item_type": item.item_type,
                            "authors": item.authors,
                            "date": item.date,
                            "tags": item.tags,
                        },
                    )
                )

            return results
        except Exception:
            return []

    def _search_pdfs(self, query: str, limit: int) -> list[UnifiedSearchResult]:
        """Search PDF content."""
        if not self.pdf_dirs:
            return []

        try:
            from nexus.research.pdf import PDFExtractor

            extractor = PDFExtractor(directories=self.pdf_dirs)
            pdf_results = extractor.search(query, limit=limit)
            results = []

            for pr in pdf_results:
                results.append(
                    UnifiedSearchResult(
                        source="pdf",
                        path=pr.path,
                        title=pr.filename,
                        snippet=pr.context[:150] + "..." if len(pr.context) > 150 else pr.context,
                        score=1.0,
                        metadata={
                            "page": pr.page,
                            "match_text": pr.match_text,
                        },
                    )
                )

            return results
        except Exception:
            return []
