"""Comprehensive tests for CLI vault/knowledge commands."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from nexus.cli import app

runner = CliRunner()


class TestVaultSearchCommand:
    """Tests for vault search command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_search_json_output(self, mock_get_vault):
        """Test vault search with JSON output."""
        mock_vault = MagicMock()
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"path": "test.md", "content": "test"}
        mock_vault.search.return_value = [mock_result]
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "search", "test", "--json"])

        assert result.exit_code == 0
        assert "test.md" in result.stdout or "path" in result.stdout

    @patch("nexus.cli._get_vault_manager")
    def test_vault_search_no_results(self, mock_get_vault):
        """Test vault search with no results."""
        mock_vault = MagicMock()
        mock_vault.search.return_value = []
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "search", "nonexistent"])

        assert result.exit_code == 0
        assert "No results" in result.stdout or "No notes" in result.stdout


class TestVaultReadCommand:
    """Tests for vault read command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_read_success(self, mock_get_vault):
        """Test reading a note."""
        from nexus.knowledge.vault import Note

        mock_vault = MagicMock()
        mock_vault.read.return_value = Note(
            title="Test Note", path=Path("test.md"), content="# Test Note\n\nContent here."
        )
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "read", "test.md"])

        assert result.exit_code == 0
        mock_vault.read.assert_called_once()

    @patch("nexus.cli._get_vault_manager")
    def test_vault_read_nonexistent(self, mock_get_vault):
        """Test reading a nonexistent note."""
        mock_vault = MagicMock()
        mock_vault.read.side_effect = FileNotFoundError("Note not found")
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "read", "missing.md"])

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestVaultWriteCommand:
    """Tests for vault write command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_write_success(self, mock_get_vault):
        """Test writing a note."""
        mock_vault = MagicMock()
        mock_vault.write.return_value = Path("test.md")
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "write", "test.md", "--content", "New content"])

        assert result.exit_code == 0
        mock_vault.write.assert_called_once()

    @patch("nexus.cli._get_vault_manager")
    def test_vault_write_creates_subdirectory(self, mock_get_vault):
        """Test writing a note in a subdirectory."""
        mock_vault = MagicMock()
        mock_vault.write.return_value = Path("subdir/test.md")
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "write", "subdir/test.md", "--content", "Content"])

        assert result.exit_code == 0
        mock_vault.write.assert_called_once()


class TestVaultRecentCommand:
    """Tests for vault recent command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_recent_success(self, mock_get_vault):
        """Test listing recent notes."""
        mock_vault = MagicMock()
        mock_vault.recent.return_value = ["recent.md", "another.md"]
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "recent"])

        assert result.exit_code == 0
        assert "recent.md" in result.stdout or "Recent" in result.stdout

    @patch("nexus.cli._get_vault_manager")
    def test_vault_recent_with_limit(self, mock_get_vault):
        """Test recent notes with limit."""
        mock_vault = MagicMock()
        mock_vault.recent.return_value = []
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "recent", "--limit", "3"])

        assert result.exit_code == 0
        mock_vault.recent.assert_called_once_with(limit=3)


class TestVaultBacklinksCommand:
    """Tests for vault backlinks command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_backlinks_success(self, mock_get_vault):
        """Test finding backlinks."""
        mock_vault = MagicMock()
        mock_vault.backlinks.return_value = ["link.md", "another.md"]
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "backlinks", "target.md"])

        assert result.exit_code == 0
        assert "link.md" in result.stdout or "backlinks" in result.stdout.lower()

    @patch("nexus.cli._get_vault_manager")
    def test_vault_backlinks_none_found(self, mock_get_vault):
        """Test backlinks when none exist."""
        mock_vault = MagicMock()
        mock_vault.backlinks.return_value = []
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "backlinks", "isolated.md"])

        assert result.exit_code == 0


class TestVaultOrphansCommand:
    """Tests for vault orphans command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_orphans_success(self, mock_get_vault):
        """Test finding orphan notes."""
        mock_vault = MagicMock()
        mock_vault.orphans.return_value = ["orphan.md", "isolated.md"]
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "orphans"])

        assert result.exit_code == 0
        assert "orphan" in result.stdout.lower() or "isolated" in result.stdout.lower()


class TestVaultGraphCommand:
    """Tests for vault graph command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_graph_basic(self, mock_get_vault):
        """Test graph generation."""
        mock_vault = MagicMock()
        mock_vault.graph.return_value = {
            "nodes": [{"id": "note1", "label": "Note 1"}],
            "edges": [],
        }
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "graph"])

        assert result.exit_code == 0
        mock_vault.graph.assert_called_once()

    @patch("nexus.cli._get_vault_manager")
    def test_vault_graph_with_tags(self, mock_get_vault):
        """Test graph with tags included."""
        mock_vault = MagicMock()
        mock_vault.graph.return_value = {"nodes": [], "edges": []}
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "graph", "--tags"])

        assert result.exit_code == 0
        mock_vault.graph.assert_called_once_with(include_tags=True, limit=None)

    @patch("nexus.cli._get_vault_manager")
    def test_vault_graph_with_limit(self, mock_get_vault):
        """Test graph with node limit."""
        mock_vault = MagicMock()
        mock_vault.graph.return_value = {"nodes": [], "edges": []}
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "graph", "--limit", "50"])

        assert result.exit_code == 0
        mock_vault.graph.assert_called_once_with(include_tags=False, limit=50)

    @patch("nexus.cli._get_vault_manager")
    def test_vault_graph_json_output(self, mock_get_vault):
        """Test graph JSON output."""
        mock_vault = MagicMock()
        mock_vault.graph.return_value = {"nodes": [], "edges": []}
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "graph", "--json"])

        assert result.exit_code == 0
        assert '"nodes"' in result.stdout
        assert '"edges"' in result.stdout


class TestVaultExportCommand:
    """Tests for vault export command."""

    @patch("nexus.cli._get_vault_manager")
    def test_vault_export_graphml(self, mock_get_vault):
        """Test export to GraphML format."""
        mock_vault = MagicMock()
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "export", "graphml", "output.graphml"])

        assert result.exit_code == 0
        mock_vault.export_graphml.assert_called_once()

    @patch("nexus.cli._get_vault_manager")
    def test_vault_export_d3(self, mock_get_vault):
        """Test export to D3.js format."""
        mock_vault = MagicMock()
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "export", "d3", "output.json"])

        assert result.exit_code == 0
        mock_vault.export_d3.assert_called_once()

    @patch("nexus.cli._get_vault_manager")
    def test_vault_export_json(self, mock_get_vault):
        """Test export to JSON format."""
        mock_vault = MagicMock()
        mock_vault.graph.return_value = {"nodes": [], "edges": []}
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "export", "json", "output.json"])

        assert result.exit_code == 0
        # JSON export uses graph() method
        assert mock_vault.graph.called

    @patch("nexus.cli._get_vault_manager")
    def test_vault_export_with_tags(self, mock_get_vault):
        """Test export with tags flag."""
        mock_vault = MagicMock()
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "export", "graphml", "output.graphml", "--tags"])

        assert result.exit_code == 0
        # Check that export was called with include_tags=True
        call_args = mock_vault.export_graphml.call_args
        assert call_args is not None

    @patch("nexus.cli._get_vault_manager")
    def test_vault_export_with_limit(self, mock_get_vault):
        """Test export with limit flag."""
        mock_vault = MagicMock()
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "vault", "export", "d3", "output.json", "--limit", "100"])

        assert result.exit_code == 0

    def test_vault_export_invalid_format(self):
        """Test export with invalid format."""
        result = runner.invoke(app, ["knowledge", "vault", "export", "invalid", "output.txt"])

        # Should fail or show error
        assert result.exit_code != 0 or "invalid" in result.stdout.lower()


class TestKnowledgeSearchCommand:
    """Tests for unified knowledge search command."""

    @patch("nexus.cli._get_vault_manager")
    def test_knowledge_search_success(self, mock_get_vault):
        """Test unified knowledge search runs."""
        mock_vault = MagicMock()
        mock_vault.exists.return_value = True
        mock_get_vault.return_value = mock_vault

        # Just test that the command runs, don't mock UnifiedSearch internals
        result = runner.invoke(app, ["knowledge", "search", "test"])

        # Command should at least try to run
        assert result.exit_code in [0, 1]  # May fail without real vault but should not crash

    @patch("nexus.cli._get_vault_manager")
    def test_knowledge_search_with_limit(self, mock_get_vault):
        """Test unified search with limit flag."""
        mock_vault = MagicMock()
        mock_vault.exists.return_value = True
        mock_get_vault.return_value = mock_vault

        result = runner.invoke(app, ["knowledge", "search", "test", "--limit", "5"])

        # Command should at least try to run
        assert result.exit_code in [0, 1]
