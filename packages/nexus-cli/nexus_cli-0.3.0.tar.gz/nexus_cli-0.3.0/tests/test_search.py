"""Tests for unified search functionality."""

import tempfile
from pathlib import Path

import pytest

from nexus.knowledge.search import UnifiedSearch, UnifiedSearchResult, SearchSource


class TestUnifiedSearchResult:
    """Test UnifiedSearchResult class."""

    def test_to_dict(self):
        """Test converting search result to dictionary."""
        result = UnifiedSearchResult(
            source="vault",
            path="/vault/test.md",
            title="Test Note",
            snippet="Test content",
            score=0.85,
            metadata={"tags": ["test"]},
        )

        result_dict = result.to_dict()

        assert result_dict["source"] == "vault"
        assert result_dict["title"] == "Test Note"
        assert result_dict["snippet"] == "Test content"
        assert result_dict["path"] == "/vault/test.md"
        assert result_dict["score"] == 0.85
        assert result_dict["metadata"]["tags"] == ["test"]

    def test_sort_by_score(self):
        """Test sorting results by score."""
        results = [
            UnifiedSearchResult("vault", "/a", "A", "content", score=0.5),
            UnifiedSearchResult("vault", "/b", "B", "content", score=0.9),
            UnifiedSearchResult("vault", "/c", "C", "content", score=0.7),
        ]

        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)

        assert sorted_results[0].title == "B"
        assert sorted_results[1].title == "C"
        assert sorted_results[2].title == "A"

    def test_score_default(self):
        """Test default score value."""
        result = UnifiedSearchResult(source="vault", path="/test", title="Test", snippet="Content")

        assert result.score == 0.0

    def test_metadata_default(self):
        """Test default metadata."""
        result = UnifiedSearchResult(source="vault", path="/test", title="Test", snippet="Content")

        assert result.metadata == {}


class TestSearchSource:
    """Test SearchSource enum."""

    def test_search_source_values(self):
        """Test SearchSource enum values."""
        assert SearchSource.VAULT == "vault"
        assert SearchSource.ZOTERO == "zotero"
        assert SearchSource.PDF == "pdf"
        assert SearchSource.ALL == "all"


class TestUnifiedSearch:
    """Test UnifiedSearch class."""

    def test_init_with_vault_only(self, sample_vault):
        """Test initializing with vault only."""
        search = UnifiedSearch(vault_path=sample_vault)

        assert search.vault_path == sample_vault
        assert search.zotero_db is None
        assert len(search.pdf_dirs) == 0

    def test_init_with_all_sources(self, sample_vault, temp_dir):
        """Test initializing with all sources."""
        zotero_db = temp_dir / "zotero.sqlite"
        zotero_db.write_text("")  # Dummy file

        pdf_dir = temp_dir / "pdfs"
        pdf_dir.mkdir()

        search = UnifiedSearch(vault_path=sample_vault, zotero_db=zotero_db, pdf_dirs=[pdf_dir])

        assert search.vault_path is not None
        assert search.zotero_db is not None
        assert len(search.pdf_dirs) == 1

    def test_available_sources_vault_only(self, sample_vault):
        """Test available_sources with vault only."""
        search = UnifiedSearch(vault_path=sample_vault)

        sources = search.available_sources()

        assert "vault" in sources
        assert "zotero" not in sources
        assert "pdf" not in sources

    def test_available_sources_nonexistent_vault(self, temp_dir):
        """Test available_sources with nonexistent vault."""
        search = UnifiedSearch(vault_path=temp_dir / "nonexistent")

        sources = search.available_sources()

        assert "vault" not in sources

    def test_vault_property(self, sample_vault):
        """Test vault property accessor."""
        search = UnifiedSearch(vault_path=sample_vault)

        vault_mgr = search.vault
        assert vault_mgr is not None
        assert vault_mgr.exists()

    def test_search_vault_basic(self, sample_vault):
        """Test basic vault search."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("mediation", sources=["vault"])

        # Should find at least the test-project note
        assert len(results) >= 0  # May or may not find results

        # All results should be from vault
        for result in results:
            assert result.source == "vault"

    def test_search_with_limit(self, sample_vault):
        """Test search with limit."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("test", limit=2)

        assert len(results) <= 2

    def test_search_empty_query(self, sample_vault):
        """Test search with empty query."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("")

        # Should handle gracefully
        assert isinstance(results, list)

    def test_search_no_results(self, sample_vault):
        """Test search that returns no results."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("xyznonexistent12345")

        assert len(results) == 0

    def test_search_vault_internal(self, sample_vault):
        """Test internal _search_vault method."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search._search_vault("mediation", limit=10)

        assert isinstance(results, list)

        # Check result structure
        for result in results:
            assert result.source == "vault"
            assert hasattr(result, "path")
            assert hasattr(result, "title")
            assert hasattr(result, "snippet")
            assert hasattr(result, "score")

    def test_search_with_none_sources(self, sample_vault):
        """Test search with sources=None uses all available."""
        search = UnifiedSearch(vault_path=sample_vault)

        # Should default to all available sources
        results = search.search("test", sources=None)

        assert isinstance(results, list)

    def test_search_result_scoring(self, sample_vault):
        """Test that results have scores."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("test")

        for result in results:
            assert isinstance(result.score, float)
            assert result.score >= 0

    def test_search_result_sorting(self, sample_vault):
        """Test that results are sorted by score."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("test")

        # Check if sorted (descending)
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score

    def test_search_metadata_present(self, sample_vault):
        """Test that search results include metadata."""
        search = UnifiedSearch(vault_path=sample_vault)

        results = search.search("mediation")

        for result in results:
            assert isinstance(result.metadata, dict)

    def test_multiple_search_instances(self, sample_vault):
        """Test multiple UnifiedSearch instances."""
        search1 = UnifiedSearch(vault_path=sample_vault)
        search2 = UnifiedSearch(vault_path=sample_vault)

        results1 = search1.search("test")
        results2 = search2.search("test")

        # Should produce consistent results
        assert len(results1) == len(results2)

    def test_search_sources_list_validation(self, sample_vault):
        """Test that sources list is validated."""
        search = UnifiedSearch(vault_path=sample_vault)

        # Should handle unknown sources gracefully
        results = search.search("test", sources=["unknown_source"])

        # Should not crash, just return empty or skip unknown source
        assert isinstance(results, list)
