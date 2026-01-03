"""Tests for PDF extraction and search."""

from nexus.research.pdf import PDFDocument, PDFSearchResult


class TestPDFDocument:
    """Test PDFDocument class."""

    def test_to_dict(self):
        """Test converting document to dictionary."""
        doc = PDFDocument(
            path="/test/paper.pdf",
            filename="paper.pdf",
            title="Research Paper",
            text="This is the full text of the paper...",
            page_count=10,
            size_bytes=1024,
        )

        result = doc.to_dict()

        assert result["filename"] == "paper.pdf"
        assert result["path"] == "/test/paper.pdf"
        assert result["title"] == "Research Paper"
        assert result["page_count"] == 10
        assert result["size_bytes"] == 1024
        assert "text_preview" in result

    def test_to_dict_no_title(self):
        """Test converting document without title."""
        doc = PDFDocument(path="/test/paper.pdf", filename="paper.pdf", text="Content", page_count=5, size_bytes=512)

        result = doc.to_dict()

        # Should use filename as title fallback
        assert result["title"] == "paper.pdf"


class TestPDFSearchResult:
    """Test PDFSearchResult class."""

    def test_to_dict(self):
        """Test converting search result to dictionary."""
        result = PDFSearchResult(
            path="/pdfs/paper.pdf",
            filename="paper.pdf",
            page=5,
            context="...relevant text from page 5...",
            match_text="mediation",
        )

        result_dict = result.to_dict()

        assert result_dict["path"] == "/pdfs/paper.pdf"
        assert result_dict["filename"] == "paper.pdf"
        assert result_dict["page"] == 5
        assert result_dict["context"] == "...relevant text from page 5..."
        assert result_dict["match_text"] == "mediation"
