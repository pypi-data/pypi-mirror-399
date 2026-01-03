"""PDF extraction and search for Nexus CLI."""

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PDFDocument:
    """A PDF document with extracted content."""

    path: str
    filename: str
    title: str = ""
    text: str = ""
    page_count: int = 0
    size_bytes: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "filename": self.filename,
            "title": self.title or self.filename,
            "page_count": self.page_count,
            "size_bytes": self.size_bytes,
            "text_preview": self.text[:500] + "..." if len(self.text) > 500 else self.text,
        }


@dataclass
class PDFSearchResult:
    """A search result from PDF content."""

    path: str
    filename: str
    page: int
    context: str
    match_text: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "filename": self.filename,
            "page": self.page,
            "context": self.context,
            "match_text": self.match_text,
        }


class PDFExtractor:
    """Extract text from PDF files using pdftotext."""

    def __init__(self, directories: list[Path] | None = None):
        """Initialize PDF extractor.

        Args:
            directories: List of directories to search for PDFs
        """
        self.directories = [Path(d).expanduser() for d in (directories or [])]
        self._pdftotext_path = shutil.which("pdftotext")

    def available(self) -> bool:
        """Check if pdftotext is available."""
        return self._pdftotext_path is not None

    def pdf_count(self) -> int:
        """Count total PDFs in configured directories."""
        count = 0
        for directory in self.directories:
            if directory.exists():
                count += len(list(directory.rglob("*.pdf")))
        return count

    def extract(
        self,
        pdf_path: Path,
        pages: str | None = None,
        layout: bool = False,
    ) -> PDFDocument:
        """Extract text from a PDF file.

        Args:
            pdf_path: Path to PDF file
            pages: Optional page range (e.g., "1-5" or "1,3,5")
            layout: Preserve layout (slower but better for tables)

        Returns:
            PDFDocument with extracted text

        Raises:
            FileNotFoundError: If PDF doesn't exist
            RuntimeError: If pdftotext not available
        """
        pdf_path = Path(pdf_path).expanduser()

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if not self.available():
            raise RuntimeError("pdftotext not installed. Run: brew install poppler")

        # Build command
        cmd = [self._pdftotext_path]

        if layout:
            cmd.append("-layout")
        else:
            # Use -raw for better text flow in multi-column papers
            cmd.append("-raw")

        # Handle page range
        first_page = None
        last_page = None
        if pages:
            if "-" in pages:
                parts = pages.split("-")
                first_page = int(parts[0])
                last_page = int(parts[1]) if len(parts) > 1 and parts[1] else None
            elif pages.isdigit():
                first_page = int(pages)
                last_page = int(pages)

        if first_page:
            cmd.extend(["-f", str(first_page)])
        if last_page:
            cmd.extend(["-l", str(last_page)])

        cmd.extend([str(pdf_path), "-"])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            text = result.stdout
        except subprocess.TimeoutExpired:
            text = "[Extraction timed out]"
        except Exception as e:
            text = f"[Extraction failed: {e}]"

        # Clean and improve text quality
        text = self._clean_text(text)

        # Get page count using pdfinfo if available
        page_count = self._get_page_count(pdf_path)

        # Try to extract title intelligently
        title = self._extract_title(text, pdf_path)

        return PDFDocument(
            path=str(pdf_path),
            filename=pdf_path.name,
            title=title,
            text=text,
            page_count=page_count,
            size_bytes=pdf_path.stat().st_size,
        )

    def _clean_text(self, text: str) -> str:
        """Clean extracted text for better readability.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text or text.startswith("["):
            return text

        # Remove multiple spaces
        text = re.sub(r"  +", " ", text)

        # Remove excessive newlines (more than 2)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Fix hyphenated words split across lines
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

        # Remove soft hyphens
        text = text.replace("\u00ad", "")

        # Fix ligatures
        text = text.replace("ﬀ", "ff")
        text = text.replace("ﬁ", "fi")
        text = text.replace("ﬂ", "fl")
        text = text.replace("ﬃ", "ffi")
        text = text.replace("ﬄ", "ffl")

        # Remove common PDF artifacts
        text = re.sub(r"\(cid:\d+\)", "", text)

        # Normalize whitespace
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line:
                lines.append(line)

        return "\n".join(lines)

    def _extract_title(self, text: str, pdf_path: Path) -> str:
        """Extract title from PDF text intelligently.

        Args:
            text: Extracted text
            pdf_path: Path to PDF

        Returns:
            Best guess at title
        """
        if not text or text.startswith("["):
            return pdf_path.stem

        lines = text.strip().split("\n")

        # Look for title in first few lines
        for i, line in enumerate(lines[:10]):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip common headers (page numbers, running heads)
            if re.match(r"^\d+$", line):
                continue
            if len(line) < 10:
                continue

            # Title is usually capitalized and reasonably long
            if len(line) > 15 and len(line) < 200 and not line.endswith(".") and line[0].isupper():
                # Clean up title
                title = re.sub(r"\s+", " ", line)

                # Remove trailing punctuation except ?!
                title = re.sub(r"[,;:]$", "", title)

                return title

        # Fallback to filename
        return pdf_path.stem

    def _get_page_count(self, pdf_path: Path) -> int:
        """Get page count using pdfinfo."""
        pdfinfo = shutil.which("pdfinfo")
        if not pdfinfo:
            return 0

        try:
            result = subprocess.run(
                [pdfinfo, str(pdf_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.split("\n"):
                if line.startswith("Pages:"):
                    return int(line.split(":")[1].strip())
        except Exception:
            pass

        return 0

    def search(
        self,
        query: str,
        limit: int = 20,
        directories: list[Path] | None = None,
        search_depth: int = 5,
    ) -> list[PDFSearchResult]:
        """Search for text in PDFs with improved context extraction.

        This implementation uses a two-pass approach:
        1. Quick filename matching
        2. Deep content search with better context

        Args:
            query: Search query
            limit: Maximum results
            directories: Override directories to search
            search_depth: Number of pages to search (default: 5)

        Returns:
            List of PDFSearchResults with ranked matches
        """
        search_dirs = directories or self.directories
        results = []

        # Compile case-insensitive pattern
        pattern = re.compile(query, re.IGNORECASE)

        # Pass 1: Quick filename matching (scored lower)
        filename_matches = []
        for directory in search_dirs:
            if not directory.exists():
                continue

            for pdf_path in directory.rglob("*.pdf"):
                if len(filename_matches) >= limit * 2:  # Get extra for ranking
                    break

                # Check filename
                if pattern.search(pdf_path.name):
                    filename_matches.append(
                        (
                            PDFSearchResult(
                                path=str(pdf_path),
                                filename=pdf_path.name,
                                page=0,
                                context=f"Filename match: {pdf_path.name}",
                                match_text=query,
                            ),
                            0.5,  # Lower score for filename-only match
                        )
                    )

        # Pass 2: Deep content search (scored higher)
        content_matches = []
        if self.available():
            searched_count = 0
            max_search = 50  # Limit to avoid long searches

            for directory in search_dirs:
                if not directory.exists():
                    continue

                for pdf_path in directory.rglob("*.pdf"):
                    if searched_count >= max_search:
                        break

                    # Skip if already matched by filename
                    if any(r[0].path == str(pdf_path) for r in filename_matches):
                        continue

                    searched_count += 1

                    try:
                        # Extract first few pages
                        doc = self.extract(pdf_path, pages=f"1-{search_depth}")

                        # Find all matches in content
                        matches = list(pattern.finditer(doc.text))

                        if matches:
                            # Take the first/best match
                            match = matches[0]

                            # Extract smart context (sentence or paragraph)
                            context = self._extract_context(doc.text, match, window=150)

                            # Calculate relevance score based on:
                            # - Number of matches
                            # - Position in document
                            # - Match in title vs body
                            score = 1.0
                            if len(matches) > 1:
                                score += 0.1 * min(len(matches) - 1, 5)
                            if match.start() < 500:  # Early in document
                                score += 0.2
                            if doc.title and query.lower() in doc.title.lower():
                                score += 0.3

                            content_matches.append(
                                (
                                    PDFSearchResult(
                                        path=str(pdf_path),
                                        filename=pdf_path.name,
                                        page=1,  # Approximate
                                        context=context,
                                        match_text=match.group(),
                                    ),
                                    score,
                                )
                            )
                    except Exception:
                        continue

        # Combine and rank results
        all_matches = content_matches + filename_matches
        all_matches.sort(key=lambda x: x[1], reverse=True)

        # Return top results without scores
        return [r[0] for r in all_matches[:limit]]

    def _extract_context(self, text: str, match: re.Match, window: int = 150) -> str:
        """Extract intelligent context around a match.

        Tries to extract a complete sentence or paragraph.

        Args:
            text: Full text
            match: Regex match object
            window: Character window size

        Returns:
            Context string
        """
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)

        # Expand to sentence boundaries if possible
        while start > 0 and text[start] not in ".!?\n":
            start -= 1
            if match.start() - start > window * 2:
                break

        while end < len(text) and text[end] not in ".!?\n":
            end += 1
            if end - match.end() > window * 2:
                break

        context = text[start:end].strip()

        # Clean up
        context = re.sub(r"\s+", " ", context)

        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context

    def list_pdfs(self, limit: int = 100) -> list[dict]:
        """List all PDFs in configured directories.

        Args:
            limit: Maximum files to list

        Returns:
            List of PDF info dicts
        """
        pdfs = []

        for directory in self.directories:
            if not directory.exists():
                continue

            for pdf_path in directory.rglob("*.pdf"):
                if len(pdfs) >= limit:
                    break

                try:
                    stat = pdf_path.stat()
                    pdfs.append(
                        {
                            "path": str(pdf_path),
                            "filename": pdf_path.name,
                            "size_bytes": stat.st_size,
                            "modified": stat.st_mtime,
                            "directory": str(pdf_path.parent),
                        }
                    )
                except Exception:
                    continue

        # Sort by modification time, newest first
        pdfs.sort(key=lambda x: x.get("modified", 0), reverse=True)

        return pdfs[:limit]

    def summarize_directories(self) -> list[dict]:
        """Summarize PDF counts per directory.

        Returns:
            List of directory summaries
        """
        summaries = []

        for directory in self.directories:
            if directory.exists():
                count = len(list(directory.rglob("*.pdf")))
                summaries.append(
                    {
                        "directory": str(directory),
                        "count": count,
                        "exists": True,
                    }
                )
            else:
                summaries.append(
                    {
                        "directory": str(directory),
                        "count": 0,
                        "exists": False,
                    }
                )

        return summaries
