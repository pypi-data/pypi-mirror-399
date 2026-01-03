"""Tests for manuscript management module."""

import pytest

from nexus.writing.manuscript import Manuscript, ManuscriptManager, ManuscriptStatus


class TestManuscriptStatus:
    """Tests for ManuscriptStatus class."""

    def test_parse_status_file(self, sample_manuscript):
        """Test parsing .STATUS file."""
        status_file = sample_manuscript / ".STATUS"
        status = ManuscriptStatus.from_file(status_file)

        assert status.status == "draft"
        assert status.priority == "2"
        assert status.progress == 45
        assert status.next_action == "Complete methods section"
        assert status.target == "JASA"

    def test_parse_missing_file(self, temp_dir):
        """Test parsing non-existent .STATUS file."""
        status = ManuscriptStatus.from_file(temp_dir / "nonexistent" / ".STATUS")

        assert status.status == "unknown"
        assert status.progress == 0


class TestManuscript:
    """Tests for Manuscript dataclass."""

    def test_status_emoji_draft(self):
        """Test status emoji for draft."""
        ms = Manuscript(name="test", path="/test", status="draft")
        assert ms.status_emoji == "📝"

    def test_status_emoji_review(self):
        """Test status emoji for under review."""
        ms = Manuscript(name="test", path="/test", status="under review")
        assert ms.status_emoji == "📬"

    def test_status_emoji_complete(self):
        """Test status emoji for complete."""
        ms = Manuscript(name="test", path="/test", status="complete")
        assert ms.status_emoji == "✅"

    def test_to_dict(self):
        """Test converting to dictionary."""
        ms = Manuscript(
            name="test-paper",
            path="/path/to/paper",
            title="Test Paper",
            status="draft",
            progress=50,
        )
        d = ms.to_dict()

        assert d["name"] == "test-paper"
        assert d["title"] == "Test Paper"
        assert d["status"] == "draft"
        assert d["progress"] == 50


class TestManuscriptManager:
    """Tests for ManuscriptManager class."""

    def test_manager_exists(self, sample_manuscript):
        """Test manager existence check."""
        manager = ManuscriptManager(sample_manuscript.parent)
        assert manager.exists() is True

    def test_list_manuscripts(self, sample_manuscript):
        """Test listing manuscripts."""
        manager = ManuscriptManager(sample_manuscript.parent)
        manuscripts = manager.list_manuscripts(include_archived=True)

        assert len(manuscripts) >= 1

        # Find our test paper
        test_paper = next((m for m in manuscripts if m.name == "test-paper"), None)
        assert test_paper is not None
        assert test_paper.status == "draft"
        assert test_paper.progress == 45

    def test_get_manuscript(self, sample_manuscript):
        """Test getting specific manuscript."""
        manager = ManuscriptManager(sample_manuscript.parent)
        ms = manager.get_manuscript("test-paper")

        assert ms is not None
        assert ms.name == "test-paper"
        assert ms.target == "JASA"

    def test_get_nonexistent_manuscript(self, sample_manuscript):
        """Test getting non-existent manuscript."""
        manager = ManuscriptManager(sample_manuscript.parent)
        ms = manager.get_manuscript("nonexistent-paper")

        assert ms is None

    def test_get_statistics(self, sample_manuscript):
        """Test getting manuscript statistics."""
        manager = ManuscriptManager(sample_manuscript.parent)
        stats = manager.get_statistics()

        assert stats["total"] >= 1
        assert "by_status" in stats
        assert "by_format" in stats
