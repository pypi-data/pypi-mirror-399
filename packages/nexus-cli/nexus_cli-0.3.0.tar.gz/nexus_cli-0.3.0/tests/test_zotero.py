"""Tests for Zotero integration."""

from nexus.research.zotero import ZoteroItem


class TestZoteroItem:
    """Test ZoteroItem class."""

    def test_to_dict(self):
        """Test converting item to dictionary."""
        item = ZoteroItem(
            item_id=1,
            key="ABCD1234",
            item_type="article",
            title="Test Article",
            authors=["Smith, J."],
            date="2024",
            tags=["test", "article"],
        )

        result = item.to_dict()

        assert result["key"] == "ABCD1234"
        assert result["item_type"] == "article"
        assert result["title"] == "Test Article"
        assert result["authors"] == ["Smith, J."]
        assert result["date"] == "2024"
        assert result["tags"] == ["test", "article"]

    def test_citation_apa_single_author(self):
        """Test APA citation with single author."""
        item = ZoteroItem(
            item_id=1, key="TEST", item_type="article", title="Test Article", authors=["Smith, John"], date="2024"
        )

        citation = item.citation_apa()

        assert "Smith, John" in citation
        assert "(2024)" in citation
        assert "Test Article" in citation

    def test_citation_apa_two_authors(self):
        """Test APA citation with two authors."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="article",
            title="Test Article",
            authors=["Smith, John", "Jones, Mary"],
            date="2024",
        )

        citation = item.citation_apa()

        assert "Smith, John & Jones, Mary" in citation

    def test_citation_apa_many_authors(self):
        """Test APA citation with many authors."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="article",
            title="Test Article",
            authors=["Smith, J.", "Jones, M.", "Brown, P.", "White, S.", "Green, T.", "Black, R."],
            date="2024",
        )

        citation = item.citation_apa()

        assert "Smith, J. et al." in citation

    def test_citation_bibtex(self):
        """Test BibTeX citation generation."""
        item = ZoteroItem(
            item_id=1,
            key="TEST",
            item_type="journalArticle",
            title="Test Article",
            authors=["Smith, John"],
            date="2024",
            doi="10.1234/test.2024",
        )

        bibtex = item.citation_bibtex()

        assert "@article{" in bibtex
        assert "title = {Test Article}" in bibtex
        assert "year = {2024}" in bibtex
        assert "doi = {10.1234/test.2024}" in bibtex
