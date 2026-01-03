"""Tests for Quarto integration."""

from nexus.teaching.quarto import QuartoProject, QuartoBuildResult


class TestQuartoProject:
    """Test QuartoProject class."""

    def test_to_dict(self):
        """Test converting project to dictionary."""
        project = QuartoProject(
            path="/projects/my-site",
            name="my-site",
            project_type="website",
            title="My Website",
            output_dir="_output",
            formats=["html", "pdf"],
        )

        result = project.to_dict()

        assert result["path"] == "/projects/my-site"
        assert result["name"] == "my-site"
        assert result["project_type"] == "website"
        assert result["title"] == "My Website"
        assert result["output_dir"] == "_output"
        assert "html" in result["formats"]
        assert "pdf" in result["formats"]

    def test_default_formats(self):
        """Test project with default formats."""
        project = QuartoProject(path="/projects/test", name="test")

        assert project.formats == []


class TestQuartoBuildResult:
    """Test QuartoBuildResult class."""

    def test_to_dict_success(self):
        """Test converting successful build result."""
        result = QuartoBuildResult(success=True, output_path="/_output/index.html", format="html", duration_seconds=2.5)

        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["output_path"] == "/_output/index.html"
        assert result_dict["format"] == "html"
        assert result_dict["duration_seconds"] == 2.5

    def test_to_dict_failure(self):
        """Test converting failed build result."""
        result = QuartoBuildResult(success=False, error="Build failed: syntax error in index.qmd", duration_seconds=1.0)

        result_dict = result.to_dict()

        assert result_dict["success"] is False
        assert "syntax error" in result_dict["error"]
