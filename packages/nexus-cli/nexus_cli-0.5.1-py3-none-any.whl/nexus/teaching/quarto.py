"""Quarto integration for Nexus CLI."""

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class QuartoProject:
    """A Quarto project."""

    path: str
    name: str
    project_type: str = "default"
    title: str = ""
    output_dir: str = ""
    formats: list[str] = None

    def __post_init__(self):
        if self.formats is None:
            self.formats = []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "name": self.name,
            "project_type": self.project_type,
            "title": self.title,
            "output_dir": self.output_dir,
            "formats": self.formats,
        }


@dataclass
class QuartoBuildResult:
    """Result of a Quarto build."""

    success: bool
    output_path: str = ""
    format: str = ""
    error: str = ""
    duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output_path": self.output_path,
            "format": self.format,
            "error": self.error,
            "duration_seconds": self.duration_seconds,
        }


class QuartoManager:
    """Manage Quarto projects and builds."""

    def __init__(self):
        """Initialize Quarto manager."""
        self._quarto_path = shutil.which("quarto")

    def available(self) -> bool:
        """Check if Quarto is available."""
        return self._quarto_path is not None

    def version(self) -> str | None:
        """Get Quarto version."""
        if not self.available():
            return None

        try:
            result = subprocess.run(
                [self._quarto_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def is_quarto_project(self, path: Path) -> bool:
        """Check if a directory is a Quarto project."""
        path = Path(path).expanduser()
        return (path / "_quarto.yml").exists() or (path / "_quarto.yaml").exists()

    def load_project(self, path: Path) -> QuartoProject | None:
        """Load a Quarto project configuration."""
        path = Path(path).expanduser()

        # Find config file
        config_file = None
        for name in ["_quarto.yml", "_quarto.yaml"]:
            if (path / name).exists():
                config_file = path / name
                break

        if not config_file:
            return None

        try:
            with open(config_file) as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return None

        project = data.get("project", {})
        book = data.get("book", {})
        website = data.get("website", {})

        # Get formats
        formats = []
        if "format" in data:
            fmt = data["format"]
            if isinstance(fmt, dict):
                formats = list(fmt.keys())
            elif isinstance(fmt, str):
                formats = [fmt]

        return QuartoProject(
            path=str(path),
            name=path.name,
            project_type=project.get("type", "default"),
            title=book.get("title") or website.get("title") or project.get("title", ""),
            output_dir=project.get("output-dir", "_site"),
            formats=formats,
        )

    def render(
        self,
        path: Path,
        output_format: str | None = None,
        to_file: str | None = None,
    ) -> QuartoBuildResult:
        """Render a Quarto document or project.

        Args:
            path: Path to .qmd file or project directory
            output_format: Output format (html, pdf, revealjs, etc.)
            to_file: Output filename

        Returns:
            QuartoBuildResult with success status
        """
        if not self.available():
            return QuartoBuildResult(
                success=False,
                error="Quarto not installed. Run: brew install quarto",
            )

        path = Path(path).expanduser()
        if not path.exists():
            return QuartoBuildResult(
                success=False,
                error=f"Path not found: {path}",
            )

        import time

        start = time.time()

        # Build command
        cmd = [self._quarto_path, "render", str(path)]

        if output_format:
            cmd.extend(["--to", output_format])

        if to_file:
            cmd.extend(["--output", to_file])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=path.parent if path.is_file() else path,
            )

            duration = time.time() - start

            if result.returncode == 0:
                # Try to find output file
                output_path = ""
                if path.is_file():
                    if output_format == "pdf":
                        output_path = str(path.with_suffix(".pdf"))
                    elif output_format in ("html", "revealjs"):
                        output_path = str(path.with_suffix(".html"))
                    else:
                        output_path = str(path.parent)
                else:
                    project = self.load_project(path)
                    if project:
                        output_path = str(path / project.output_dir)

                return QuartoBuildResult(
                    success=True,
                    output_path=output_path,
                    format=output_format or "default",
                    duration_seconds=duration,
                )
            else:
                return QuartoBuildResult(
                    success=False,
                    error=result.stderr or result.stdout,
                    duration_seconds=duration,
                )

        except subprocess.TimeoutExpired:
            return QuartoBuildResult(
                success=False,
                error="Build timed out after 5 minutes",
            )
        except Exception as e:
            return QuartoBuildResult(
                success=False,
                error=str(e),
            )

    def preview(self, path: Path, port: int = 4200) -> dict:
        """Start Quarto preview server.

        Note: This starts a background process. Returns info about the server.

        Args:
            path: Path to .qmd file or project directory
            port: Port number for preview server

        Returns:
            Dictionary with server info
        """
        if not self.available():
            return {
                "success": False,
                "error": "Quarto not installed. Run: brew install quarto",
            }

        path = Path(path).expanduser()
        if not path.exists():
            return {
                "success": False,
                "error": f"Path not found: {path}",
            }

        cmd = [self._quarto_path, "preview", str(path), "--port", str(port)]

        try:
            # Start in background (non-blocking)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=path.parent if path.is_file() else path,
            )

            return {
                "success": True,
                "pid": process.pid,
                "url": f"http://localhost:{port}",
                "command": " ".join(cmd),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def list_formats(self, path: Path) -> list[str]:
        """List available output formats for a Quarto project."""
        project = self.load_project(path)
        if project:
            return project.formats

        # Default formats if not a project
        return ["html", "pdf", "docx"]

    def check_dependencies(self, path: Path) -> dict:
        """Check if all dependencies are available for a project.

        Args:
            path: Path to project

        Returns:
            Dictionary with dependency status
        """
        path = Path(path).expanduser()
        deps = {
            "quarto": self.available(),
            "quarto_version": self.version(),
        }

        # Check for format-specific dependencies
        project = self.load_project(path)
        if project:
            # PDF requires tinytex or latex
            if "pdf" in project.formats or "beamer" in project.formats:
                deps["latex"] = shutil.which("pdflatex") is not None
                deps["tinytex"] = shutil.which("tlmgr") is not None

            # Typst requires typst
            if "typst" in project.formats:
                deps["typst"] = shutil.which("typst") is not None

        return deps

    def clean(self, path: Path) -> dict:
        """Clean Quarto build artifacts.

        Args:
            path: Path to project

        Returns:
            Dictionary with cleaned items
        """
        path = Path(path).expanduser()
        cleaned = []

        # Common build directories to clean
        build_dirs = ["_site", "_book", "_freeze", "_output"]

        for dirname in build_dirs:
            dir_path = path / dirname
            if dir_path.exists() and dir_path.is_dir():
                try:
                    shutil.rmtree(dir_path)
                    cleaned.append(str(dir_path))
                except Exception:
                    pass

        # Clean .quarto directory
        quarto_dir = path / ".quarto"
        if quarto_dir.exists():
            try:
                shutil.rmtree(quarto_dir)
                cleaned.append(str(quarto_dir))
            except Exception:
                pass

        return {
            "success": True,
            "cleaned": cleaned,
            "count": len(cleaned),
        }

    def export(
        self,
        path: Path,
        output_format: str,
        output_dir: Path | None = None,
    ) -> QuartoBuildResult:
        """Export a document to a specific format.

        Wrapper around render with better output handling.

        Args:
            path: Path to .qmd file
            output_format: Target format
            output_dir: Output directory (optional)

        Returns:
            QuartoBuildResult
        """
        path = Path(path).expanduser()

        if output_dir:
            output_dir = Path(output_dir).expanduser()
            output_dir.mkdir(parents=True, exist_ok=True)

        result = self.render(path, output_format=output_format)

        # Move output to target directory if specified
        if result.success and output_dir and result.output_path:
            output_path = Path(result.output_path)
            if output_path.exists() and output_path.is_file():
                target = output_dir / output_path.name
                shutil.copy2(output_path, target)
                result.output_path = str(target)

        return result
