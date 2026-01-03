"""Tests for CLI commands."""

import pytest
from typer.testing import CliRunner

from nexus.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_version(self):
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_help(self):
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Knowledge workflow CLI" in result.stdout

    def test_doctor_runs(self):
        """Test doctor command runs."""
        result = runner.invoke(app, ["doctor"])
        # Should run without error (exit code 0)
        assert result.exit_code == 0
        assert "Nexus Health Check" in result.stdout

    def test_config_runs(self):
        """Test config command runs."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configuration" in result.stdout


class TestKnowledgeCommands:
    """Tests for knowledge subcommands."""

    def test_knowledge_help(self):
        """Test knowledge --help."""
        result = runner.invoke(app, ["knowledge", "--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout
        assert "vault" in result.stdout

    def test_vault_help(self):
        """Test vault --help."""
        result = runner.invoke(app, ["knowledge", "vault", "--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout
        assert "recent" in result.stdout


class TestResearchCommands:
    """Tests for research subcommands."""

    def test_research_help(self):
        """Test research --help."""
        result = runner.invoke(app, ["research", "--help"])
        assert result.exit_code == 0
        assert "zotero" in result.stdout
        assert "pdf" in result.stdout

    def test_zotero_help(self):
        """Test zotero --help."""
        result = runner.invoke(app, ["research", "zotero", "--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout
        assert "cite" in result.stdout


class TestTeachCommands:
    """Tests for teaching subcommands."""

    def test_teach_help(self):
        """Test teach --help."""
        result = runner.invoke(app, ["teach", "--help"])
        assert result.exit_code == 0
        assert "course" in result.stdout
        assert "quarto" in result.stdout

    def test_course_help(self):
        """Test course --help."""
        result = runner.invoke(app, ["teach", "course", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "show" in result.stdout


class TestWriteCommands:
    """Tests for writing subcommands."""

    def test_write_help(self):
        """Test write --help."""
        result = runner.invoke(app, ["write", "--help"])
        assert result.exit_code == 0
        assert "manuscript" in result.stdout
        assert "bib" in result.stdout

    def test_manuscript_help(self):
        """Test manuscript --help."""
        result = runner.invoke(app, ["write", "manuscript", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "show" in result.stdout
        assert "stats" in result.stdout

    def test_bib_help(self):
        """Test bib --help."""
        result = runner.invoke(app, ["write", "bib", "--help"])
        assert result.exit_code == 0
        assert "list" in result.stdout
        assert "check" in result.stdout
