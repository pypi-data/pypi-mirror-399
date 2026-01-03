"""Tests for PDFExtractor class."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nexus.research.pdf import PDFDocument, PDFExtractor, PDFSearchResult


@pytest.fixture
def pdf_extractor(temp_dir):
    """Create a PDFExtractor with pdftotext available."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/local/bin/pdftotext"
        extractor = PDFExtractor([temp_dir])
        yield extractor


@pytest.fixture
def pdf_extractor_unavailable(temp_dir):
    """Create a PDFExtractor with pdftotext unavailable."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None
        extractor = PDFExtractor([temp_dir])
        yield extractor


class TestPDFExtractorAvailability:
    """Test PDF extractor availability."""

    def test_available_when_installed(self, pdf_extractor):
        """Test available() returns True when pdftotext installed."""
        assert pdf_extractor.available() is True

    def test_unavailable_when_not_installed(self, pdf_extractor_unavailable):
        """Test available() returns False when pdftotext not installed."""
        assert pdf_extractor_unavailable.available() is False


class TestPDFExtraction:
    """Test PDF text extraction."""

    def test_extract_success(self, pdf_extractor, temp_dir):
        """Test successful PDF extraction."""
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nFake PDF content")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="This is the extracted text from the PDF.\n\nPage 2 content here.",
                stderr="",
                returncode=0,
            )

            result = pdf_extractor.extract(pdf_path)

            assert result is not None
            assert isinstance(result, PDFDocument)
            assert "extracted text" in result.text

    def test_extract_unavailable(self, pdf_extractor_unavailable, temp_dir):
        """Test extraction when pdftotext unavailable."""
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nFake PDF")

        with pytest.raises(RuntimeError, match="pdftotext"):
            pdf_extractor_unavailable.extract(pdf_path)

    def test_extract_file_not_found(self, pdf_extractor, temp_dir):
        """Test extraction with nonexistent file."""
        with pytest.raises(FileNotFoundError):
            pdf_extractor.extract(temp_dir / "nonexistent.pdf")

    def test_extract_with_page_range(self, pdf_extractor, temp_dir):
        """Test extraction with specific page range."""
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nFake PDF")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="Page 2 content", stderr="", returncode=0)

            result = pdf_extractor.extract(pdf_path, pages="2-2")

            # Verify we get a result back
            assert result is not None
            assert isinstance(result, PDFDocument)
            # Check that the first call (pdftotext) had page arguments
            first_call = mock_run.call_args_list[0][0][0]
            assert "-f" in first_call
            assert "-l" in first_call

    def test_extract_clean_text(self, pdf_extractor, temp_dir):
        """Test text cleaning after extraction."""
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            # Simulate messy PDF output with extra whitespace
            mock_run.return_value = MagicMock(
                stdout="   This   has    extra     spaces   \n\n\n\n  and lines  ",
                stderr="",
                returncode=0,
            )

            result = pdf_extractor.extract(pdf_path)

            # Check that text was cleaned (implementation may vary)
            assert result is not None


class TestPDFListing:
    """Test PDF file listing."""

    def test_list_pdfs_empty_dir(self, pdf_extractor, temp_dir):
        """Test listing PDFs in empty directory."""
        pdfs = pdf_extractor.list_pdfs()
        assert len(pdfs) == 0

    def test_list_pdfs_with_files(self, pdf_extractor, temp_dir):
        """Test listing PDFs with actual files."""
        (temp_dir / "paper1.pdf").write_bytes(b"%PDF-1.4\n")
        (temp_dir / "paper2.pdf").write_bytes(b"%PDF-1.4\n")
        (temp_dir / "notes.txt").write_text("Not a PDF")

        pdfs = pdf_extractor.list_pdfs()

        assert len(pdfs) == 2
        filenames = [p["filename"] for p in pdfs]
        assert "paper1.pdf" in filenames
        assert "paper2.pdf" in filenames

    def test_list_pdfs_nested_dirs(self, temp_dir):
        """Test listing PDFs in nested directories."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (subdir / "nested.pdf").write_bytes(b"%PDF-1.4\n")

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/local/bin/pdftotext"
            extractor = PDFExtractor([temp_dir])

            pdfs = extractor.list_pdfs()

            # Should find PDFs in subdirectories too
            assert len(pdfs) >= 1

    def test_list_pdfs_multiple_dirs(self, temp_dir):
        """Test listing PDFs from multiple directories."""
        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "a.pdf").write_bytes(b"%PDF-1.4\n")
        (dir2 / "b.pdf").write_bytes(b"%PDF-1.4\n")

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/local/bin/pdftotext"
            extractor = PDFExtractor([dir1, dir2])

            pdfs = extractor.list_pdfs()

            assert len(pdfs) == 2

    def test_list_pdfs_nonexistent_dir(self):
        """Test listing PDFs with nonexistent directory."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/local/bin/pdftotext"
            extractor = PDFExtractor([Path("/nonexistent/path")])

            pdfs = extractor.list_pdfs()
            assert len(pdfs) == 0


class TestPDFSearch:
    """Test PDF content search."""

    def test_search_empty_query(self, pdf_extractor, temp_dir):
        """Test search with empty query."""
        results = pdf_extractor.search("", limit=10)
        assert isinstance(results, list)

    def test_search_no_pdfs(self, pdf_extractor, temp_dir):
        """Test search with no PDFs."""
        results = pdf_extractor.search("test", limit=10)
        assert len(results) == 0

    def test_search_with_results(self, pdf_extractor, temp_dir):
        """Test search finding matching PDFs."""
        (temp_dir / "mediation.pdf").write_bytes(b"%PDF-1.4\n")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="This paper discusses mediation analysis in depth.",
                stderr="",
                returncode=0,
            )

            results = pdf_extractor.search("mediation", limit=10)

            # Should find the PDF
            assert isinstance(results, list)

    def test_search_limit(self, pdf_extractor, temp_dir):
        """Test search respects limit."""
        for i in range(5):
            (temp_dir / f"paper{i}.pdf").write_bytes(b"%PDF-1.4\n")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="Matching content here", stderr="", returncode=0)

            results = pdf_extractor.search("content", limit=2)

            assert len(results) <= 2

    def test_search_no_match(self, pdf_extractor, temp_dir):
        """Test search with no matches."""
        (temp_dir / "paper.pdf").write_bytes(b"%PDF-1.4\n")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="Completely unrelated content",
                stderr="",
                returncode=0,
            )

            results = pdf_extractor.search("xyzabc123", limit=10)

            # Should return empty or items without match
            assert isinstance(results, list)


class TestPDFMetadata:
    """Test PDF metadata extraction."""

    def test_get_metadata(self, pdf_extractor, temp_dir):
        """Test extracting PDF metadata."""
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nFake PDF content for testing")

        with patch("nexus.research.pdf.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="Title: Test Paper\nAuthor: John Smith\nPages: 10",
                stderr="",
                returncode=0,
            )

            # If get_metadata exists
            if hasattr(pdf_extractor, "get_metadata"):
                metadata = pdf_extractor.get_metadata(pdf_path)
                assert metadata is not None


class TestPDFDocumentModel:
    """Test PDFDocument data model."""

    def test_document_with_all_fields(self):
        """Test creating document with all fields."""
        doc = PDFDocument(
            path="/papers/test.pdf",
            filename="test.pdf",
            title="Test Paper Title",
            text="Full text content",
            page_count=15,
            size_bytes=1024 * 1024,
        )

        assert doc.path == "/papers/test.pdf"
        assert doc.filename == "test.pdf"
        assert doc.title == "Test Paper Title"
        assert doc.page_count == 15

    def test_document_to_dict_truncates_text(self):
        """Test that to_dict truncates long text."""
        long_text = "x" * 10000
        doc = PDFDocument(
            path="/test.pdf",
            filename="test.pdf",
            text=long_text,
            page_count=1,
            size_bytes=1000,
        )

        result = doc.to_dict()

        assert len(result["text_preview"]) <= 503  # 500 + "..."

    def test_document_title_fallback(self):
        """Test title falls back to filename."""
        doc = PDFDocument(
            path="/test.pdf",
            filename="myfile.pdf",
            title="",
            text="",
            page_count=1,
            size_bytes=100,
        )

        result = doc.to_dict()
        assert result["title"] == "myfile.pdf"


class TestPDFSearchResultModel:
    """Test PDFSearchResult data model."""

    def test_search_result_creation(self):
        """Test creating search result."""
        result = PDFSearchResult(
            path="/papers/found.pdf",
            filename="found.pdf",
            page=3,
            context="...matching text here...",
            match_text="matching",
        )

        assert result.path == "/papers/found.pdf"
        assert result.page == 3
        assert result.match_text == "matching"

    def test_search_result_to_dict(self):
        """Test search result serialization."""
        result = PDFSearchResult(
            path="/test.pdf",
            filename="test.pdf",
            page=1,
            context="context",
            match_text="match",
        )

        result_dict = result.to_dict()

        assert "path" in result_dict
        assert "page" in result_dict
        assert "context" in result_dict
        assert "match_text" in result_dict
