"""Tests for bibliography management module."""

import pytest

from nexus.writing.bibliography import BibEntry, BibFileParser, BibliographyManager


class TestBibEntry:
    """Tests for BibEntry class."""

    def test_format_apa_single_author(self):
        """Test APA formatting with single author."""
        entry = BibEntry(
            key="Test2024",
            entry_type="article",
            title="Test Article",
            authors=["Smith, John"],
            year="2024",
        )
        apa = entry.format_apa()

        assert "Smith, John" in apa
        assert "(2024)" in apa
        assert "Test Article" in apa

    def test_format_apa_two_authors(self):
        """Test APA formatting with two authors."""
        entry = BibEntry(
            key="Test2024",
            entry_type="article",
            title="Test Article",
            authors=["Smith, John", "Doe, Jane"],
            year="2024",
        )
        apa = entry.format_apa()

        assert "Smith, John & Doe, Jane" in apa

    def test_format_apa_many_authors(self):
        """Test APA formatting with many authors (et al.)."""
        entry = BibEntry(
            key="Test2024",
            entry_type="article",
            title="Test Article",
            authors=["A", "B", "C", "D", "E", "F", "G"],
            year="2024",
        )
        apa = entry.format_apa()

        assert "et al." in apa

    def test_to_dict(self):
        """Test converting to dictionary."""
        entry = BibEntry(
            key="Test2024",
            entry_type="article",
            title="Test Article",
            authors=["Smith, John"],
            year="2024",
            doi="10.1234/test",
        )
        d = entry.to_dict()

        assert d["key"] == "Test2024"
        assert d["entry_type"] == "article"
        assert d["doi"] == "10.1234/test"


class TestBibFileParser:
    """Tests for BibFileParser class."""

    def test_parse_bibtex(self, temp_dir, sample_bib_content):
        """Test parsing BibTeX file."""
        bib_file = temp_dir / "test.bib"
        bib_file.write_text(sample_bib_content)

        parser = BibFileParser()
        entries = parser.parse_file(bib_file)

        assert len(entries) == 3

        # Check article
        article = next((e for e in entries if e.key == "Test2024"), None)
        assert article is not None
        assert article.entry_type == "article"
        assert len(article.authors) == 2
        assert article.year == "2024"

        # Check book
        book = next((e for e in entries if e.key == "Book2023"), None)
        assert book is not None
        assert book.entry_type == "book"

    def test_parse_nonexistent_file(self, temp_dir):
        """Test parsing non-existent file."""
        parser = BibFileParser()
        entries = parser.parse_file(temp_dir / "nonexistent.bib")

        assert entries == []

    def test_parse_authors(self):
        """Test author string parsing."""
        parser = BibFileParser()

        # Single author
        authors = parser._parse_authors("Smith, John")
        assert authors == ["John Smith"]

        # Multiple authors
        authors = parser._parse_authors("Smith, John and Doe, Jane")
        assert len(authors) == 2
        assert "John Smith" in authors
        assert "Jane Doe" in authors


class TestBibliographyManager:
    """Tests for BibliographyManager class."""

    def test_find_bib_files(self, sample_manuscript):
        """Test finding .bib files."""
        manager = BibliographyManager()
        bib_files = manager.find_bib_files(sample_manuscript)

        assert len(bib_files) >= 1
        assert any(f.name == "references.bib" for f in bib_files)

    def test_get_manuscript_bibliography(self, sample_manuscript):
        """Test getting manuscript bibliography."""
        manager = BibliographyManager()
        entries = manager.get_manuscript_bibliography(sample_manuscript)

        assert len(entries) >= 4  # Our sample has 4 entries

    def test_find_cited_keys_pandoc(self):
        """Test finding Pandoc-style citations."""
        manager = BibliographyManager()
        content = "See @MacKinnon2008 and also [@VanderWeele2015; @Baron1986]."

        keys = manager.find_cited_keys(content)

        assert "MacKinnon2008" in keys
        assert "VanderWeele2015" in keys
        assert "Baron1986" in keys

    def test_find_cited_keys_latex(self):
        """Test finding LaTeX-style citations."""
        manager = BibliographyManager()
        content = r"See \cite{MacKinnon2008} and \citep{VanderWeele2015}."

        keys = manager.find_cited_keys(content)

        assert "MacKinnon2008" in keys
        assert "VanderWeele2015" in keys

    def test_check_citations(self, sample_manuscript):
        """Test citation checking."""
        manager = BibliographyManager()
        result = manager.check_citations(sample_manuscript)

        assert "cited_count" in result
        assert "bibliography_count" in result
        assert "missing" in result
        assert "unused" in result

        # We have 4 cited, 4 in bib, 1 unused (UnusedEntry), 1 missing (Sobel1982)
        assert result["bibliography_count"] == 4
        assert "UnusedEntry" in result["unused"]

    def test_search_bibliography(self, sample_manuscript):
        """Test searching bibliography."""
        manager = BibliographyManager()

        # Search for MacKinnon
        results = manager.search_bibliography(sample_manuscript, "MacKinnon")
        assert len(results) >= 1
        assert any(e.key == "MacKinnon2008" for e in results)

        # Search for something not present
        results = manager.search_bibliography(sample_manuscript, "NonexistentAuthor")
        assert len(results) == 0
