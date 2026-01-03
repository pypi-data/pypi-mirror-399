"""Validation tests for data models and input handling."""

from nexus.knowledge.vault import Note
from nexus.knowledge.vault import SearchResult as VaultSearchResult
from nexus.research.pdf import PDFDocument, PDFSearchResult
from nexus.research.zotero import ZoteroItem
from nexus.teaching.courses import Course, CourseStatus
from nexus.teaching.quarto import QuartoBuildResult, QuartoProject
from nexus.writing.bibliography import BibEntry
from nexus.writing.manuscript import Manuscript, ManuscriptStatus


class TestVaultDataModels:
    """Test vault data model validation."""

    def test_note_minimal(self):
        """Test Note with minimal data."""
        note = Note(path="/vault/note.md", title="Test Note", content="Content")

        assert note.path == "/vault/note.md"
        assert note.title == "Test Note"
        assert len(note.links) == 0
        assert len(note.tags) == 0

    def test_note_to_dict(self):
        """Test Note serialization."""
        note = Note(
            path="/vault/note.md",
            title="Test Note",
            content="This is a long content" * 20,
            links=["other-note"],
            tags=["tag1", "tag2"],
            frontmatter={"key": "value"},
        )

        result = note.to_dict()

        assert result["path"] == "/vault/note.md"
        assert result["title"] == "Test Note"
        assert result["links"] == ["other-note"]
        assert result["tags"] == ["tag1", "tag2"]
        assert result["frontmatter"]["key"] == "value"
        # Content should be truncated
        assert len(result["content_preview"]) <= 203  # 200 + "..."

    def test_vault_search_result(self):
        """Test VaultSearchResult model."""
        result = VaultSearchResult(
            path="/vault/note.md", line_number=42, content="Matched line content", match_text="content"
        )

        assert result.path == "/vault/note.md"
        assert result.line_number == 42

        result_dict = result.to_dict()
        assert result_dict["line_number"] == 42


class TestZoteroDataModels:
    """Test Zotero data model validation."""

    def test_zotero_item_minimal(self):
        """Test ZoteroItem with minimal required fields."""
        item = ZoteroItem(item_id=1, key="ABC123", item_type="article", title="Test Article")

        assert item.item_id == 1
        assert item.key == "ABC123"
        assert len(item.authors) == 0
        assert len(item.tags) == 0

    def test_zotero_item_full(self):
        """Test ZoteroItem with all fields."""
        item = ZoteroItem(
            item_id=1,
            key="ABC123",
            item_type="article",
            title="Test Article",
            authors=["Smith, J.", "Jones, M."],
            date="2024",
            abstract="This is an abstract" * 20,  # Long abstract
            doi="10.1234/test",
            url="https://example.com",
            tags=["tag1", "tag2"],
            collections=["col1"],
        )

        result = item.to_dict()

        assert result["key"] == "ABC123"
        assert len(result["authors"]) == 2
        # Abstract should be truncated
        assert len(result["abstract"]) <= 203  # 200 + "..."

    def test_zotero_citation_no_authors(self):
        """Test citation generation with no authors."""
        item = ZoteroItem(item_id=1, key="ABC123", item_type="article", title="Test Article", date="2024")

        citation = item.citation_apa()
        assert "Unknown" in citation
        assert "2024" in citation

    def test_zotero_citation_no_date(self):
        """Test citation with no date."""
        item = ZoteroItem(item_id=1, key="ABC123", item_type="article", title="Test Article", authors=["Smith, J."])

        citation = item.citation_apa()
        assert "n.d." in citation

    def test_zotero_bibtex_invalid_type(self):
        """Test BibTeX with unmapped item type."""
        item = ZoteroItem(
            item_id=1, key="ABC123", item_type="unknownType", title="Test", authors=["Smith, J."], date="2024"
        )

        bibtex = item.citation_bibtex()
        # Should default to @misc
        assert "@misc{" in bibtex


class TestPDFDataModels:
    """Test PDF data model validation."""

    def test_pdf_document_minimal(self):
        """Test PDFDocument with minimal data."""
        doc = PDFDocument(path="/pdfs/test.pdf", filename="test.pdf")

        assert doc.path == "/pdfs/test.pdf"
        assert doc.filename == "test.pdf"
        assert doc.page_count == 0

    def test_pdf_document_to_dict(self):
        """Test PDFDocument serialization."""
        doc = PDFDocument(
            path="/pdfs/test.pdf",
            filename="test.pdf",
            title="Test Paper",
            text="Long text content" * 50,
            page_count=10,
            size_bytes=1024000,
        )

        result = doc.to_dict()

        assert result["filename"] == "test.pdf"
        assert result["title"] == "Test Paper"
        assert result["page_count"] == 10
        # Text preview should be truncated
        assert len(result["text_preview"]) <= 503

    def test_pdf_search_result_validation(self):
        """Test PDFSearchResult validation."""
        result = PDFSearchResult(
            path="/pdfs/test.pdf", filename="test.pdf", page=5, context="Context around match", match_text="match"
        )

        assert result.page == 5
        assert result.match_text == "match"


class TestTeachingDataModels:
    """Test teaching domain data models."""

    def test_course_status_parsing(self):
        """Test CourseStatus model."""
        status = CourseStatus(status="active", priority=1, progress=50, next="Prepare lecture", week=7)

        assert status.status == "active"
        assert status.week == 7

    def test_course_to_dict(self):
        """Test Course serialization."""
        course = Course(
            name="STAT 440",
            path="/courses/stat-440",
            title="Regression Analysis",
            status=CourseStatus(status="active", priority=1, progress=50, next="", week=1),
        )

        result = course.to_dict()

        assert result["name"] == "STAT 440"
        assert result["title"] == "Regression Analysis"
        assert "status" in result

    def test_quarto_project_defaults(self):
        """Test QuartoProject with defaults."""
        project = QuartoProject(path="/projects/site", name="site")

        assert project.formats == []
        assert project.project_type == "default"

    def test_quarto_build_result_success(self):
        """Test QuartoBuildResult for successful build."""
        result = QuartoBuildResult(success=True, output_path="/_output/index.html", format="html", duration_seconds=2.5)

        assert result.success is True
        assert result.error == ""

        result_dict = result.to_dict()
        assert result_dict["success"] is True

    def test_quarto_build_result_failure(self):
        """Test QuartoBuildResult for failed build."""
        result = QuartoBuildResult(success=False, error="Syntax error on line 42", duration_seconds=1.0)

        assert result.success is False
        assert "Syntax error" in result.error


class TestWritingDataModels:
    """Test writing domain data models."""

    def test_manuscript_status_validation(self):
        """Test ManuscriptStatus parsing."""
        status = ManuscriptStatus(
            status="draft", priority="2", progress=45, next_action="Complete methods", target="JASA"
        )

        assert status.status == "draft"
        assert status.target == "JASA"
        assert status.progress == 45

    def test_manuscript_status_emoji(self):
        """Test manuscript status emoji."""
        ms = Manuscript(name="test-paper", path="/manuscripts/test-paper", status="draft")

        assert ms.status_emoji in ["📝", "📬", "✏️", "✅", "⏸️", "🔥", "💡", "📄"]

    def test_manuscript_to_dict(self):
        """Test Manuscript serialization."""
        ms = Manuscript(
            name="test-paper",
            path="/manuscripts/test-paper",
            title="Research Paper",
            authors=["Smith, J."],
            status="draft",
            target="JASA",
        )

        result = ms.to_dict()

        assert result["name"] == "test-paper"
        assert result["title"] == "Research Paper"
        assert len(result["authors"]) == 1

    def test_bib_entry_single_author(self):
        """Test BibEntry with single author."""
        entry = BibEntry(
            key="Smith2024", entry_type="article", title="Test Article", authors=["Smith, John"], year="2024"
        )

        assert entry.key == "Smith2024"
        assert len(entry.authors) == 1

    def test_bib_entry_format_apa(self):
        """Test APA formatting."""
        entry = BibEntry(
            key="Smith2024",
            entry_type="article",
            title="Test Article",
            authors=["Smith, John"],
            year="2024",
            journal="Test Journal",
        )

        formatted = entry.format_apa()

        assert "Smith, John" in formatted
        assert "2024" in formatted
        assert "Test Article" in formatted

    def test_bib_entry_multiple_authors(self):
        """Test bibliography with multiple authors."""
        entry = BibEntry(
            key="Test2024",
            entry_type="article",
            title="Multi-Author Paper",
            authors=["Smith, J.", "Jones, M.", "Brown, P."],
            year="2024",
        )

        formatted = entry.format_apa()
        # Should include all authors
        assert "Smith" in formatted
        assert "Jones" in formatted
        assert "Brown" in formatted


class TestInputValidation:
    """Test input validation and error handling."""

    def test_empty_strings(self):
        """Test handling of empty strings."""
        note = Note(path="", title="", content="")
        assert note.path == ""
        assert note.title == ""

    def test_special_characters_in_paths(self):
        """Test paths with special characters."""
        note = Note(path="/vault/note with spaces & special-chars.md", title="Test", content="Content")
        assert "spaces & special-chars" in note.path

    def test_unicode_content(self):
        """Test Unicode content handling."""
        note = Note(path="/vault/note.md", title="Tëst Nøtē 中文", content="Unicode content: café, naïve, 日本語")

        assert "café" in note.content
        assert "中文" in note.title

    def test_very_long_content(self):
        """Test handling of very long content."""
        long_content = "x" * 100000
        note = Note(path="/vault/note.md", title="Long Note", content=long_content)

        result = note.to_dict()
        # Should be truncated in preview
        assert len(result["content_preview"]) <= 203

    def test_list_fields_empty(self):
        """Test empty list fields."""
        item = ZoteroItem(item_id=1, key="ABC", item_type="article", title="Test", authors=[], tags=[], collections=[])

        assert len(item.authors) == 0
        assert len(item.tags) == 0

    def test_optional_fields_none(self):
        """Test optional fields as None."""
        doc = PDFDocument(
            path="/test.pdf",
            filename="test.pdf",
            title="",  # Empty title
            text="",  # Empty text
            page_count=0,
            size_bytes=0,
        )

        result = doc.to_dict()
        # Should use filename as fallback
        assert result["title"] == "test.pdf"
