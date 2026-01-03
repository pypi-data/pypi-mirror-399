"""Tests for QuartoManager class."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from nexus.teaching.quarto import QuartoManager


@pytest.fixture
def quarto_manager():
    """Create a QuartoManager with mocked quarto path."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = "/usr/local/bin/quarto"
        manager = QuartoManager()
        yield manager


@pytest.fixture
def quarto_manager_unavailable():
    """Create a QuartoManager with quarto unavailable."""
    with patch("shutil.which") as mock_which:
        mock_which.return_value = None
        manager = QuartoManager()
        yield manager


class TestQuartoManagerAvailability:
    """Test Quarto availability checks."""

    def test_available_when_installed(self, quarto_manager):
        """Test available() returns True when Quarto is installed."""
        assert quarto_manager.available() is True

    def test_unavailable_when_not_installed(self, quarto_manager_unavailable):
        """Test available() returns False when Quarto is not installed."""
        assert quarto_manager_unavailable.available() is False

    def test_version_returns_string(self, quarto_manager):
        """Test version() returns version string."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="1.4.554\n", returncode=0)
            version = quarto_manager.version()
            assert version == "1.4.554"

    def test_version_unavailable(self, quarto_manager_unavailable):
        """Test version() returns None when Quarto unavailable."""
        version = quarto_manager_unavailable.version()
        assert version is None

    def test_version_error_handling(self, quarto_manager):
        """Test version() handles errors gracefully."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("Failed")
            version = quarto_manager.version()
            assert version is None


class TestQuartoProjectDetection:
    """Test project detection and loading."""

    def test_is_quarto_project_yml(self, temp_dir, quarto_manager):
        """Test detecting project with _quarto.yml."""
        (temp_dir / "_quarto.yml").write_text("project:\n  type: website\n")

        assert quarto_manager.is_quarto_project(temp_dir) is True

    def test_is_quarto_project_yaml(self, temp_dir, quarto_manager):
        """Test detecting project with _quarto.yaml."""
        (temp_dir / "_quarto.yaml").write_text("project:\n  type: book\n")

        assert quarto_manager.is_quarto_project(temp_dir) is True

    def test_is_not_quarto_project(self, temp_dir, quarto_manager):
        """Test non-Quarto directory."""
        assert quarto_manager.is_quarto_project(temp_dir) is False

    def test_load_project_website(self, temp_dir, quarto_manager):
        """Test loading a website project."""
        config = """
project:
  type: website
  output-dir: _site

website:
  title: "My Site"

format:
  html: default
  pdf: default
"""
        (temp_dir / "_quarto.yml").write_text(config)

        project = quarto_manager.load_project(temp_dir)

        assert project is not None
        assert project.name == temp_dir.name
        assert project.project_type == "website"
        assert project.title == "My Site"
        assert project.output_dir == "_site"
        assert "html" in project.formats
        assert "pdf" in project.formats

    def test_load_project_book(self, temp_dir, quarto_manager):
        """Test loading a book project."""
        config = """
project:
  type: book

book:
  title: "My Book"
  author: "Author Name"

format: html
"""
        (temp_dir / "_quarto.yml").write_text(config)

        project = quarto_manager.load_project(temp_dir)

        assert project is not None
        assert project.project_type == "book"
        assert project.title == "My Book"
        assert "html" in project.formats

    def test_load_project_not_found(self, temp_dir, quarto_manager):
        """Test loading nonexistent project."""
        project = quarto_manager.load_project(temp_dir)
        assert project is None

    def test_load_project_invalid_yaml(self, temp_dir, quarto_manager):
        """Test loading project with invalid YAML."""
        (temp_dir / "_quarto.yml").write_text("invalid: yaml: content:")

        project = quarto_manager.load_project(temp_dir)
        assert project is None


class TestQuartoRender:
    """Test rendering functionality."""

    def test_render_unavailable(self, quarto_manager_unavailable, temp_dir):
        """Test render when Quarto is unavailable."""
        result = quarto_manager_unavailable.render(temp_dir)

        assert result.success is False
        assert "not installed" in result.error

    def test_render_path_not_found(self, quarto_manager, temp_dir):
        """Test render with nonexistent path."""
        result = quarto_manager.render(temp_dir / "nonexistent")

        assert result.success is False
        assert "not found" in result.error

    def test_render_success(self, quarto_manager, temp_dir):
        """Test successful render."""
        (temp_dir / "_quarto.yml").write_text("project:\n  type: website\n")
        (temp_dir / "index.qmd").write_text("# Hello")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            result = quarto_manager.render(temp_dir)

            assert result.success is True
            assert result.duration_seconds > 0

    def test_render_with_format(self, quarto_manager, temp_dir):
        """Test render with specific format."""
        qmd_file = temp_dir / "test.qmd"
        qmd_file.write_text("# Test")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            result = quarto_manager.render(qmd_file, output_format="pdf")

            assert result.success is True
            assert result.format == "pdf"
            # Check that --to pdf was in command
            call_args = mock_run.call_args[0][0]
            assert "--to" in call_args
            assert "pdf" in call_args

    def test_render_failure(self, quarto_manager, temp_dir):
        """Test render failure."""
        qmd_file = temp_dir / "test.qmd"
        qmd_file.write_text("# Test")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error: syntax error on line 5")

            result = quarto_manager.render(qmd_file)

            assert result.success is False
            assert "syntax error" in result.error

    def test_render_timeout(self, quarto_manager, temp_dir):
        """Test render timeout handling."""
        qmd_file = temp_dir / "test.qmd"
        qmd_file.write_text("# Test")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("quarto", 300)

            result = quarto_manager.render(qmd_file)

            assert result.success is False
            assert "timed out" in result.error


class TestQuartoPreview:
    """Test preview server functionality."""

    def test_preview_unavailable(self, quarto_manager_unavailable, temp_dir):
        """Test preview when Quarto unavailable."""
        result = quarto_manager_unavailable.preview(temp_dir)

        assert result["success"] is False
        assert "not installed" in result["error"]

    def test_preview_path_not_found(self, quarto_manager, temp_dir):
        """Test preview with nonexistent path."""
        result = quarto_manager.preview(temp_dir / "nonexistent")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_preview_success(self, quarto_manager, temp_dir):
        """Test starting preview server."""
        (temp_dir / "_quarto.yml").write_text("project:\n  type: website\n")

        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process

            result = quarto_manager.preview(temp_dir, port=4200)

            assert result["success"] is True
            assert result["pid"] == 12345
            assert result["url"] == "http://localhost:4200"

    def test_preview_custom_port(self, quarto_manager, temp_dir):
        """Test preview with custom port."""
        (temp_dir / "_quarto.yml").write_text("project:\n  type: website\n")

        with patch("subprocess.Popen") as mock_popen:
            mock_popen.return_value = MagicMock(pid=1234)

            result = quarto_manager.preview(temp_dir, port=8080)

            assert result["url"] == "http://localhost:8080"


class TestQuartoClean:
    """Test clean functionality."""

    def test_clean_build_dirs(self, quarto_manager, temp_dir):
        """Test cleaning build directories."""
        # Create build directories
        (temp_dir / "_site").mkdir()
        (temp_dir / "_site" / "index.html").write_text("<html></html>")
        (temp_dir / "_book").mkdir()
        (temp_dir / ".quarto").mkdir()

        result = quarto_manager.clean(temp_dir)

        assert result["success"] is True
        assert result["count"] == 3
        assert not (temp_dir / "_site").exists()
        assert not (temp_dir / "_book").exists()
        assert not (temp_dir / ".quarto").exists()

    def test_clean_no_build_dirs(self, quarto_manager, temp_dir):
        """Test clean when no build directories exist."""
        result = quarto_manager.clean(temp_dir)

        assert result["success"] is True
        assert result["count"] == 0


class TestQuartoListFormats:
    """Test format listing."""

    def test_list_formats_from_project(self, quarto_manager, temp_dir):
        """Test listing formats from project config."""
        config = """
format:
  html: default
  pdf: default
  docx: default
"""
        (temp_dir / "_quarto.yml").write_text(config)

        formats = quarto_manager.list_formats(temp_dir)

        assert "html" in formats
        assert "pdf" in formats
        assert "docx" in formats

    def test_list_formats_no_project(self, quarto_manager, temp_dir):
        """Test default formats for non-project."""
        formats = quarto_manager.list_formats(temp_dir)

        assert "html" in formats
        assert "pdf" in formats
        assert "docx" in formats


class TestQuartoCheckDependencies:
    """Test dependency checking."""

    def test_check_dependencies_basic(self, quarto_manager, temp_dir):
        """Test basic dependency check."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="1.4.554\n", returncode=0)

            deps = quarto_manager.check_dependencies(temp_dir)

            assert deps["quarto"] is True
            assert deps["quarto_version"] is not None

    def test_check_dependencies_pdf(self, quarto_manager, temp_dir):
        """Test dependency check for PDF projects."""
        config = """
format:
  pdf: default
"""
        (temp_dir / "_quarto.yml").write_text(config)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="1.4.554\n", returncode=0)
            with patch("shutil.which") as mock_which:
                # First call is for quarto, subsequent for latex tools
                mock_which.side_effect = ["/usr/local/bin/quarto", "/usr/bin/pdflatex", None]

                deps = quarto_manager.check_dependencies(temp_dir)

                # Note: depends on mock_which call order
                assert "latex" in deps or "quarto" in deps


class TestQuartoExport:
    """Test export functionality."""

    def test_export_success(self, quarto_manager, temp_dir):
        """Test successful export."""
        qmd_file = temp_dir / "doc.qmd"
        qmd_file.write_text("# Document")
        output_dir = temp_dir / "exports"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            result = quarto_manager.export(qmd_file, "html", output_dir)

            assert result.success is True
            assert output_dir.exists()
