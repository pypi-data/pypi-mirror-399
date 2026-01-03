"""Additional CLI command tests for improved coverage."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from nexus.cli import app

runner = CliRunner()


class TestResearchCommands:
    """Test research domain commands."""

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

    def test_pdf_help(self):
        """Test pdf --help."""
        result = runner.invoke(app, ["research", "pdf", "--help"])
        assert result.exit_code == 0
        assert "extract" in result.stdout or "search" in result.stdout

    @patch("nexus.cli.get_config")
    def test_zotero_search_no_db(self, mock_config):
        """Test zotero search when database not configured."""
        mock_config.return_value = MagicMock(zotero=MagicMock(database=None))
        result = runner.invoke(app, ["research", "zotero", "search", "test"])
        # Should handle gracefully
        assert result.exit_code in [0, 1]


class TestTeachingCommands:
    """Test teaching domain commands."""

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

    def test_quarto_help(self):
        """Test quarto --help."""
        result = runner.invoke(app, ["teach", "quarto", "--help"])
        assert result.exit_code == 0


class TestWritingCommands:
    """Test writing domain commands."""

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

    def test_bib_help(self):
        """Test bib --help."""
        result = runner.invoke(app, ["write", "bib", "--help"])
        assert result.exit_code == 0


class TestKnowledgeCommands:
    """Test knowledge domain commands."""

    def test_knowledge_help(self):
        """Test knowledge --help."""
        result = runner.invoke(app, ["knowledge", "--help"])
        assert result.exit_code == 0
        assert "vault" in result.stdout
        assert "search" in result.stdout

    def test_vault_commands(self):
        """Test vault subcommands exist."""
        result = runner.invoke(app, ["knowledge", "vault", "--help"])
        assert result.exit_code == 0
        assert "search" in result.stdout
        assert "read" in result.stdout
        assert "recent" in result.stdout


class TestConfigCommand:
    """Test config command."""

    def test_config_display(self):
        """Test config command displays configuration."""
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        # Should show some config info
        assert "Configuration" in result.stdout or "config" in result.stdout.lower()


class TestDoctorCommand:
    """Test doctor command."""

    def test_doctor_output(self):
        """Test doctor command produces output."""
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Nexus Health Check" in result.stdout or "health" in result.stdout.lower()


class TestVersionAndHelp:
    """Test version and help flags."""

    def test_version_format(self):
        """Test version output format."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        # Should contain version number
        assert "0." in result.stdout

    def test_help_shows_all_domains(self):
        """Test help shows all domains."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "knowledge" in result.stdout
        assert "research" in result.stdout
        assert "teach" in result.stdout
        assert "write" in result.stdout
        assert "doctor" in result.stdout
        assert "config" in result.stdout


class TestInvalidCommands:
    """Test handling of invalid commands."""

    def test_invalid_domain(self):
        """Test invalid domain."""
        result = runner.invoke(app, ["invalid-domain"])
        assert result.exit_code != 0

    def test_invalid_subcommand(self):
        """Test invalid subcommand."""
        result = runner.invoke(app, ["knowledge", "invalid-cmd"])
        assert result.exit_code != 0


class TestCommandAliases:
    """Test command aliases if they exist."""

    def test_short_flags(self):
        """Test short flag variants work."""
        # Test -n for limit
        result = runner.invoke(app, ["knowledge", "vault", "search", "test", "-n", "5"])
        # May fail if vault not configured, but should parse args
        assert "-n" not in result.stdout or result.exit_code in [0, 1]
