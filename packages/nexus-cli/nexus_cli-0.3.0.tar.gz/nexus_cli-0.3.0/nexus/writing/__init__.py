"""Writing domain - Manuscripts, bibliography, LaTeX."""

from nexus.writing.bibliography import BibEntry, BibliographyManager
from nexus.writing.manuscript import Manuscript, ManuscriptManager, ManuscriptStatus

__all__ = [
    "Manuscript",
    "ManuscriptManager",
    "ManuscriptStatus",
    "BibEntry",
    "BibliographyManager",
]
