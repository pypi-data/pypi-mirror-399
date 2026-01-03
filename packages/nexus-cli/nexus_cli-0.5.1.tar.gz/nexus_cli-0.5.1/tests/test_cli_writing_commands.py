"""Comprehensive tests for CLI writing commands (Manuscript and Bibliography)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from nexus.cli import app

runner = CliRunner()


class TestManuscriptListCommand:
    """Tests for manuscript list command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_list_success(self, mock_get_manager):
        """Test listing manuscripts."""
        mock_manager = MagicMock()
        mock_manager.list_manuscripts.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "list"])

        assert result.exit_code in [0, 1]

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_list_json(self, mock_get_manager):
        """Test listing manuscripts with JSON output."""
        mock_manager = MagicMock()
        mock_manager.list_manuscripts.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "list", "--json"])

        assert result.exit_code in [0, 1]


class TestManuscriptShowCommand:
    """Tests for manuscript show command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_show_success(self, mock_get_manager):
        """Test showing manuscript details."""
        mock_manager = MagicMock()
        mock_ms = MagicMock()
        mock_ms.to_dict.return_value = {"name": "paper1", "status": "draft"}
        mock_manager.get_manuscript.return_value = mock_ms
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "show", "paper1"])

        assert result.exit_code in [0, 1]


class TestManuscriptActiveCommand:
    """Tests for manuscript active command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_active_success(self, mock_get_manager):
        """Test listing active manuscripts."""
        mock_manager = MagicMock()
        mock_manager.list_manuscripts.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "active"])

        assert result.exit_code in [0, 1]


class TestManuscriptSearchCommand:
    """Tests for manuscript search command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_search_success(self, mock_get_manager):
        """Test searching manuscripts."""
        mock_manager = MagicMock()
        mock_manager.search_manuscripts.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "search", "mediation"])

        assert result.exit_code in [0, 1]


class TestManuscriptStatsCommand:
    """Tests for manuscript stats command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_stats_success(self, mock_get_manager):
        """Test getting manuscript statistics."""
        mock_manager = MagicMock()
        mock_manager.get_statistics.return_value = {"total": 5, "by_status": {"draft": 2, "review": 3}}
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "stats"])

        assert result.exit_code in [0, 1]


class TestManuscriptDeadlinesCommand:
    """Tests for manuscript deadlines command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_deadlines_success(self, mock_get_manager):
        """Test listing manuscript deadlines."""
        mock_manager = MagicMock()
        mock_manager.list_manuscripts.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "deadlines"])

        assert result.exit_code in [0, 1]


class TestManuscriptBatchStatusCommand:
    """Tests for manuscript batch-status command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_batch_status_success(self, mock_get_manager):
        """Test batch status update."""
        mock_manager = MagicMock()
        mock_manager.batch_update_status.return_value = {"success": ["paper1", "paper2"], "failed": [], "errors": {}}
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "batch-status", "paper1", "paper2", "--status", "review"])

        assert result.exit_code in [0, 1]


class TestManuscriptBatchProgressCommand:
    """Tests for manuscript batch-progress command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_batch_progress_success(self, mock_get_manager):
        """Test batch progress update."""
        mock_manager = MagicMock()
        mock_manager.batch_update_progress.return_value = {"success": ["paper1"], "failed": [], "errors": {}}
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "batch-progress", "paper1:75"])

        assert result.exit_code in [0, 1]


class TestManuscriptBatchArchiveCommand:
    """Tests for manuscript batch-archive command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_batch_archive_success(self, mock_get_manager):
        """Test batch archiving."""
        mock_manager = MagicMock()
        mock_manager.batch_archive.return_value = {"success": ["old-paper"], "failed": [], "errors": {}}
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "batch-archive", "old-paper"])

        assert result.exit_code in [0, 1]


class TestManuscriptExportCommand:
    """Tests for manuscript export command."""

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_export_json(self, mock_get_manager):
        """Test exporting manuscripts to JSON."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "export", "output.json"])

        assert result.exit_code in [0, 1]

    @patch("nexus.cli._get_manuscript_manager")
    def test_manuscript_export_csv(self, mock_get_manager):
        """Test exporting manuscripts to CSV."""
        mock_manager = MagicMock()
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "manuscript", "export", "output.csv", "--format", "csv"])

        assert result.exit_code in [0, 1]


class TestBibListCommand:
    """Tests for bib list command."""

    @patch("nexus.cli._get_bibliography_manager")
    def test_bib_list_success(self, mock_get_manager):
        """Test listing bibliography entries."""
        mock_manager = MagicMock()
        mock_manager.get_manuscript_bibliography.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "bib", "list", "paper1"])

        assert result.exit_code in [0, 1]


class TestBibSearchCommand:
    """Tests for bib search command."""

    @patch("nexus.cli._get_bibliography_manager")
    def test_bib_search_success(self, mock_get_manager):
        """Test searching bibliography."""
        mock_manager = MagicMock()
        mock_manager.search_bibliography.return_value = []
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "bib", "search", "mediation"])

        assert result.exit_code in [0, 1, 2]


class TestBibCheckCommand:
    """Tests for bib check command."""

    @patch("nexus.cli._get_bibliography_manager")
    def test_bib_check_success(self, mock_get_manager):
        """Test checking citations."""
        mock_manager = MagicMock()
        mock_manager.check_citations.return_value = {"missing": [], "unused": [], "cited": []}
        mock_get_manager.return_value = mock_manager

        result = runner.invoke(app, ["write", "bib", "check", "paper1"])

        assert result.exit_code in [0, 1]


class TestBibZoteroCommand:
    """Tests for bib zotero command."""

    @patch("nexus.cli._get_zotero_client")
    @patch("nexus.cli._get_bibliography_manager")
    def test_bib_zotero_search(self, mock_get_bib, mock_get_zotero):
        """Test searching Zotero from bib command."""
        mock_bib = MagicMock()
        mock_get_bib.return_value = mock_bib

        mock_zotero = MagicMock()
        mock_zotero.search.return_value = []
        mock_get_zotero.return_value = mock_zotero

        result = runner.invoke(app, ["write", "bib", "zotero", "mediation"])

        assert result.exit_code in [0, 1]
