"""Knowledge domain - Vault, search, and connections."""

from nexus.knowledge.search import SearchSource, UnifiedSearch, UnifiedSearchResult
from nexus.knowledge.vault import Note, SearchResult, VaultManager

__all__ = [
    "VaultManager",
    "Note",
    "SearchResult",
    "UnifiedSearch",
    "UnifiedSearchResult",
    "SearchSource",
]
