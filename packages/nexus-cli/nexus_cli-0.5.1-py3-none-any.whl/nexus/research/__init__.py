"""Research domain - Zotero, PDFs, literature."""

from nexus.research.pdf import PDFDocument, PDFExtractor, PDFSearchResult
from nexus.research.zotero import ZoteroClient, ZoteroItem

__all__ = [
    "ZoteroClient",
    "ZoteroItem",
    "PDFExtractor",
    "PDFDocument",
    "PDFSearchResult",
]
