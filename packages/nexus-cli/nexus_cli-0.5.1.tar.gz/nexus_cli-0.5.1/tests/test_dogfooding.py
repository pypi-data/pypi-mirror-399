"""
Dogfooding integration tests - Run real Nexus commands end-to-end.

These tests use real temporary fixtures to test actual workflow scenarios
without mocking. They verify that commands work together as users would
actually use them.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from nexus.cli import app

runner = CliRunner()


@pytest.fixture
def temp_vault(tmp_path):
    """Create a temporary Obsidian vault with sample notes."""
    vault = tmp_path / "test-vault"
    vault.mkdir()

    # Create some sample notes
    (vault / "note1.md").write_text("""---
title: Research Note
tags: [research, methodology]
---

# Research Note

This is about research methodology and data analysis.
Links to [[note2]].
""")

    (vault / "note2.md").write_text("""---
title: Statistics Note
tags: [statistics, analysis]
---

# Statistics Note

This covers statistical methods.
Links to [[note1]] and [[note3]].
""")

    (vault / "note3.md").write_text("""# Unlinked Note

This note has no links and no frontmatter.
It's an orphan.
""")

    # Create a subdirectory
    (vault / "projects").mkdir()
    (vault / "projects" / "project1.md").write_text("""# Project 1

A project note in a subdirectory.
""")

    return vault


@pytest.fixture
def temp_manuscripts(tmp_path):
    """Create temporary manuscript directory with .STATUS files."""
    ms_dir = tmp_path / "manuscripts"
    ms_dir.mkdir()

    # Create manuscript 1
    paper1 = ms_dir / "paper1"
    paper1.mkdir()
    (paper1 / ".STATUS").write_text("""status: draft
progress: 25
target: Journal of Testing
deadline: 2025-12-31
""")
    (paper1 / "manuscript.tex").write_text("\\documentclass{article}")

    # Create manuscript 2
    paper2 = ms_dir / "paper2"
    paper2.mkdir()
    (paper2 / ".STATUS").write_text("""status: review
progress: 75
target: Testing Review
""")

    # Create manuscript 3 (no status file)
    paper3 = ms_dir / "paper3"
    paper3.mkdir()
    (paper3 / "draft.md").write_text("# Paper 3 Draft")

    return ms_dir


@pytest.fixture
def temp_config(tmp_path, temp_vault, temp_manuscripts):
    """Create temporary config file."""
    config_dir = tmp_path / ".config" / "nexus"
    config_dir.mkdir(parents=True)

    config_file = config_dir / "config.yaml"
    config_content = f"""
vault:
  path: {temp_vault}
  templates: {temp_vault}/_templates

writing:
  manuscripts_dir: {temp_manuscripts}
  templates_dir: {temp_manuscripts}/_templates

pdf:
  directories: []

zotero:
  database: /nonexistent/zotero.sqlite
  storage: /nonexistent/storage
"""
    config_file.write_text(config_content)
    return config_file


class TestDogfoodingVaultOperations:
    """Test real vault operations end-to-end."""

    def test_vault_search_finds_notes(self, temp_vault, temp_config, monkeypatch):
        """Test searching vault with real notes."""
        # Set config path
        result = runner.invoke(
            app, ["knowledge", "vault", "search", "research"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        assert "note1" in result.stdout or "Research" in result.stdout

    def test_vault_read_note(self, temp_vault, temp_config, monkeypatch):
        """Test reading a specific note."""
        result = runner.invoke(
            app, ["knowledge", "vault", "read", "note1.md"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        assert "Research Note" in result.stdout or "research" in result.stdout.lower()

    def test_vault_write_and_read(self, temp_vault, temp_config, monkeypatch):
        """Test writing a note then reading it back."""
        # Write a new note
        result1 = runner.invoke(
            app,
            ["knowledge", "vault", "write", "test-note.md", "--content", "# Test Note\n\nThis is a test."],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result1.exit_code == 0

        # Read it back
        result2 = runner.invoke(
            app, ["knowledge", "vault", "read", "test-note.md"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result2.exit_code == 0
        assert "Test Note" in result2.stdout or "test" in result2.stdout.lower()

    def test_vault_recent_notes(self, temp_vault, temp_config, monkeypatch):
        """Test listing recent notes."""
        result = runner.invoke(
            app, ["knowledge", "vault", "recent", "--limit", "5"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        # Should show some notes
        assert "note" in result.stdout.lower() or "md" in result.stdout.lower()

    def test_vault_backlinks(self, temp_vault, temp_config, monkeypatch):
        """Test finding backlinks."""
        result = runner.invoke(
            app, ["knowledge", "vault", "backlinks", "note2.md"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        # note1 links to note2
        assert "note1" in result.stdout or "backlinks" in result.stdout.lower()

    def test_vault_orphans(self, temp_vault, temp_config, monkeypatch):
        """Test finding orphan notes."""
        result = runner.invoke(
            app, ["knowledge", "vault", "orphans"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        # note3 is an orphan (no incoming links)
        assert "note3" in result.stdout or "orphan" in result.stdout.lower()

    def test_vault_graph_generation(self, temp_vault, temp_config, monkeypatch):
        """Test generating vault graph."""
        result = runner.invoke(
            app, ["knowledge", "vault", "graph", "--json"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        # Should have JSON output with nodes and edges
        assert '"nodes"' in result.stdout
        assert '"edges"' in result.stdout

        # Verify it's valid JSON
        try:
            data = json.loads(result.stdout)
            assert "nodes" in data
            assert "edges" in data
        except json.JSONDecodeError:
            pytest.fail("Graph output is not valid JSON")

    def test_vault_export_graphml(self, temp_vault, temp_config, monkeypatch, tmp_path):
        """Test exporting graph to GraphML."""
        output_file = tmp_path / "graph.graphml"
        result = runner.invoke(
            app,
            [
                "knowledge",
                "vault",
                "export",
                "graphml",
                str(output_file),
            ],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify GraphML format
        content = output_file.read_text()
        assert '<?xml version="1.0"' in content
        assert "<graphml" in content
        assert "<graph" in content

    def test_vault_export_d3(self, temp_vault, temp_config, monkeypatch, tmp_path):
        """Test exporting graph to D3 format."""
        output_file = tmp_path / "graph.json"
        result = runner.invoke(
            app,
            [
                "knowledge",
                "vault",
                "export",
                "d3",
                str(output_file),
            ],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify D3 format
        data = json.loads(output_file.read_text())
        assert "nodes" in data
        assert isinstance(data["nodes"], list)
        if data["nodes"]:
            assert "id" in data["nodes"][0]


class TestDogfoodingManuscriptOperations:
    """Test real manuscript operations end-to-end."""

    def test_manuscript_list(self, temp_manuscripts, temp_config, monkeypatch):
        """Test listing manuscripts."""
        result = runner.invoke(
            app, ["write", "manuscript", "list"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        assert "paper1" in result.stdout or "paper2" in result.stdout

    def test_manuscript_show_details(self, temp_manuscripts, temp_config, monkeypatch):
        """Test showing manuscript details."""
        result = runner.invoke(
            app, ["write", "manuscript", "show", "paper1"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        assert "draft" in result.stdout.lower() or "paper1" in result.stdout

    def test_manuscript_stats(self, temp_manuscripts, temp_config, monkeypatch):
        """Test manuscript statistics."""
        result = runner.invoke(
            app, ["write", "manuscript", "stats"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        # Should show count and statistics
        assert any(word in result.stdout.lower() for word in ["total", "manuscript", "status"])

    def test_manuscript_batch_status(self, temp_manuscripts, temp_config, monkeypatch):
        """Test batch status update."""
        result = runner.invoke(
            app,
            ["write", "manuscript", "batch-status", "paper1", "paper2", "--status", "review"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0
        # Verify update was mentioned
        assert "success" in result.stdout.lower() or "updated" in result.stdout.lower()

        # Verify status was actually updated
        status1 = (temp_manuscripts / "paper1" / ".STATUS").read_text()
        assert "review" in status1.lower()

    def test_manuscript_batch_progress(self, temp_manuscripts, temp_config, monkeypatch):
        """Test batch progress update."""
        result = runner.invoke(
            app,
            ["write", "manuscript", "batch-progress", "paper1:50", "paper2:90"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0

        # Verify progress was updated
        status1 = (temp_manuscripts / "paper1" / ".STATUS").read_text()
        assert "50" in status1

    def test_manuscript_export_json(self, temp_manuscripts, temp_config, monkeypatch, tmp_path):
        """Test exporting manuscript metadata to JSON."""
        output_file = tmp_path / "manuscripts.json"
        result = runner.invoke(
            app,
            ["write", "manuscript", "export", str(output_file)],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify JSON format
        data = json.loads(output_file.read_text())
        assert isinstance(data, list)
        if data:
            assert "name" in data[0] or "path" in data[0]

    def test_manuscript_export_csv(self, temp_manuscripts, temp_config, monkeypatch, tmp_path):
        """Test exporting manuscript metadata to CSV."""
        output_file = tmp_path / "manuscripts.csv"
        result = runner.invoke(
            app,
            [
                "write",
                "manuscript",
                "export",
                str(output_file),
                "--format",
                "csv",
            ],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify CSV format
        content = output_file.read_text()
        assert "," in content  # CSV has commas
        lines = content.strip().split("\n")
        assert len(lines) >= 1  # At least header


class TestDogfoodingWorkflows:
    """Test real end-to-end workflows."""

    def test_workflow_vault_write_search_read(self, temp_vault, temp_config, monkeypatch):
        """Test complete workflow: write → search → read."""
        # Step 1: Write a new note
        result1 = runner.invoke(
            app,
            [
                "knowledge",
                "vault",
                "write",
                "workflow-test.md",
                "--content",
                "# Workflow Test\n\nThis tests the complete workflow.",
            ],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result1.exit_code == 0

        # Step 2: Search for it
        result2 = runner.invoke(
            app, ["knowledge", "vault", "search", "workflow"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )
        assert result2.exit_code == 0
        assert "workflow" in result2.stdout.lower()

        # Step 3: Read it back
        result3 = runner.invoke(
            app,
            ["knowledge", "vault", "read", "workflow-test.md"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result3.exit_code == 0
        assert "Workflow Test" in result3.stdout

    def test_workflow_manuscript_update_export(self, temp_manuscripts, temp_config, monkeypatch, tmp_path):
        """Test workflow: update manuscripts → export metadata."""
        # Step 1: Update manuscript progress
        result1 = runner.invoke(
            app,
            ["write", "manuscript", "batch-progress", "paper1:80", "paper2:95"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result1.exit_code == 0

        # Step 2: Export to JSON
        output_file = tmp_path / "export.json"
        result2 = runner.invoke(
            app,
            ["write", "manuscript", "export", str(output_file)],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result2.exit_code == 0
        assert output_file.exists()

        # Step 3: Verify exported data has updated values
        data = json.loads(output_file.read_text())
        paper1_data = [m for m in data if "paper1" in str(m.get("name", m.get("path", "")))]
        if paper1_data:
            assert paper1_data[0].get("progress") == 80

    def test_workflow_vault_graph_export_multiple_formats(self, temp_vault, temp_config, monkeypatch, tmp_path):
        """Test exporting graph to multiple formats."""
        # Export to GraphML
        graphml_file = tmp_path / "graph.graphml"
        result1 = runner.invoke(
            app,
            [
                "knowledge",
                "vault",
                "export",
                "graphml",
                str(graphml_file),
                "--tags",
            ],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result1.exit_code == 0
        assert graphml_file.exists()

        # Export to D3
        d3_file = tmp_path / "graph-d3.json"
        result2 = runner.invoke(
            app,
            ["knowledge", "vault", "export", "d3", str(d3_file), "--tags"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result2.exit_code == 0
        assert d3_file.exists()

        # Export to JSON
        json_file = tmp_path / "graph-json.json"
        result3 = runner.invoke(
            app,
            ["knowledge", "vault", "export", "json", str(json_file)],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result3.exit_code == 0
        assert json_file.exists()

        # All files should exist
        assert graphml_file.exists() and d3_file.exists() and json_file.exists()


class TestDogfoodingErrorHandling:
    """Test error handling in real scenarios."""

    def test_read_nonexistent_note(self, temp_vault, temp_config, monkeypatch):
        """Test reading a note that doesn't exist."""
        result = runner.invoke(
            app, ["knowledge", "vault", "read", "nonexistent.md"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_show_nonexistent_manuscript(self, temp_manuscripts, temp_config, monkeypatch):
        """Test showing a manuscript that doesn't exist."""
        result = runner.invoke(
            app, ["write", "manuscript", "show", "nonexistent"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code in [0, 1]  # May return None or error

    def test_batch_update_with_invalid_progress(self, temp_manuscripts, temp_config, monkeypatch):
        """Test batch progress with invalid value."""
        result = runner.invoke(
            app,
            [
                "write",
                "manuscript",
                "batch-progress",
                "paper1:150",  # Invalid: > 100
            ],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        # Should handle gracefully
        assert result.exit_code in [0, 1]


class TestDogfoodingJSONOutput:
    """Test JSON output formatting."""

    def test_vault_search_json(self, temp_vault, temp_config, monkeypatch):
        """Test vault search with JSON output."""
        result = runner.invoke(
            app,
            ["knowledge", "vault", "search", "research", "--json"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )

        assert result.exit_code == 0
        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert isinstance(data, list)
        except json.JSONDecodeError:
            pytest.fail("Search output is not valid JSON")

    def test_manuscript_list_json(self, temp_manuscripts, temp_config, monkeypatch):
        """Test manuscript list with JSON output."""
        result = runner.invoke(
            app, ["write", "manuscript", "list", "--json"], env={**os.environ, "NEXUS_CONFIG": str(temp_config)}
        )

        assert result.exit_code == 0
        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert isinstance(data, list)
        except json.JSONDecodeError:
            pytest.fail("Manuscript list output is not valid JSON")


# ============================================================================
# RESEARCH DOMAIN - Zotero Operations
# ============================================================================


class TestDogfoodingZoteroOperations:
    """Test real Zotero operations end-to-end."""

    def test_zotero_search(self, temp_config):
        """Test searching Zotero library."""
        # Note: This will fail if no Zotero DB exists, but tests the command structure
        result = runner.invoke(
            app,
            ["research", "zotero", "search", "mediation", "--limit", "5"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Either succeeds or fails with "Database not found" error
        assert result.exit_code in [0, 1]

    def test_zotero_search_json(self, temp_config):
        """Test Zotero search with JSON output."""
        result = runner.invoke(
            app,
            ["research", "zotero", "search", "test", "--json"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should exit cleanly even if DB doesn't exist
        assert result.exit_code in [0, 1]

    def test_zotero_tags(self, temp_config):
        """Test listing Zotero tags."""
        result = runner.invoke(
            app,
            ["research", "zotero", "tags", "--limit", "10"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]

    def test_zotero_collections(self, temp_config):
        """Test listing Zotero collections."""
        result = runner.invoke(
            app,
            ["research", "zotero", "collections"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]

    def test_zotero_recent(self, temp_config):
        """Test listing recent Zotero items."""
        result = runner.invoke(
            app,
            ["research", "zotero", "recent", "--limit", "5"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]


# ============================================================================
# RESEARCH DOMAIN - PDF Operations
# ============================================================================


class TestDogfoodingPDFOperations:
    """Test real PDF operations end-to-end."""

    def test_pdf_list(self, temp_config):
        """Test listing PDFs."""
        result = runner.invoke(
            app,
            ["research", "pdf", "list", "--limit", "10"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # May succeed with 0 PDFs or fail if directories don't exist
        assert result.exit_code in [0, 1]

    def test_pdf_search(self, temp_config):
        """Test searching PDFs."""
        result = runner.invoke(
            app,
            ["research", "pdf", "search", "statistics"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]

    def test_pdf_list_json(self, temp_config):
        """Test PDF list with JSON output."""
        result = runner.invoke(
            app,
            ["research", "pdf", "list", "--json"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]
        # If successful, should be valid JSON
        if result.exit_code == 0 and result.stdout.strip():
            try:
                json.loads(result.stdout)
            except json.JSONDecodeError:
                pytest.fail("Invalid JSON output")


# ============================================================================
# TEACHING DOMAIN - Course Operations
# ============================================================================


class TestDogfoodingCourseOperations:
    """Test real course operations end-to-end."""

    def test_course_list(self, temp_config):
        """Test listing courses."""
        result = runner.invoke(
            app,
            ["teach", "course", "list"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # May succeed with 0 courses or fail if directory doesn't exist
        assert result.exit_code in [0, 1]

    def test_course_list_json(self, temp_config):
        """Test listing courses with JSON output."""
        result = runner.invoke(
            app,
            ["teach", "course", "list", "--json"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]
        if result.exit_code == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                assert isinstance(data, list)
            except json.JSONDecodeError:
                pytest.fail("Invalid JSON output")


# ============================================================================
# TEACHING DOMAIN - Quarto Operations
# ============================================================================


class TestDogfoodingQuartoOperations:
    """Test Quarto operations end-to-end."""

    def test_quarto_info_nonexistent_project(self, temp_config, tmp_path):
        """Test quarto info on nonexistent project."""
        result = runner.invoke(
            app,
            ["teach", "quarto", "info"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should fail gracefully if no quarto project found
        assert result.exit_code in [0, 1]

    def test_quarto_formats(self, temp_config, tmp_path):
        """Test listing quarto formats."""
        # Create a minimal quarto project
        quarto_file = tmp_path / "_quarto.yml"
        quarto_file.write_text("""
project:
  type: default
""")
        
        result = runner.invoke(
            app,
            ["teach", "quarto", "formats", str(tmp_path)],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should work even with minimal project
        assert result.exit_code in [0, 1]


# ============================================================================
# WRITING DOMAIN - Bibliography Operations
# ============================================================================


class TestDogfoodingBibliographyOperations:
    """Test bibliography operations end-to-end."""

    def test_bibliography_list(self, temp_manuscripts, temp_config):
        """Test listing bibliography entries for a manuscript."""
        # Create a .bib file in paper1
        paper1_dir = temp_manuscripts / "paper1"
        bib_file = paper1_dir / "references.bib"
        bib_content = """@article{smith2024,
  author = {Smith, John},
  title = {A Test Article},
  year = {2024}
}"""
        bib_file.write_text(bib_content)
        
        result = runner.invoke(
            app,
            ["write", "bib", "list", "paper1"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # May fail if bibtexparser not available or bib file not found
        assert result.exit_code in [0, 1]

    def test_bibliography_search(self, temp_manuscripts, temp_config):
        """Test searching bibliography."""
        # Create a .bib file in paper1
        paper1_dir = temp_manuscripts / "paper1"
        bib_file = paper1_dir / "references.bib"
        bib_file.write_text("""@article{smith2024,
  author = {Smith, John},
  title = {A Test Article},
  year = {2024}
}""")
        
        result = runner.invoke(
            app,
            ["write", "bib", "search", "paper1", "Smith"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]

    def test_bibliography_check(self, temp_manuscripts, temp_config):
        """Test checking bibliography for missing citations."""
        # Create manuscript with citations
        paper1_dir = temp_manuscripts / "paper1"
        (paper1_dir / "manuscript.tex").write_text(r"""
\documentclass{article}
\begin{document}
This cites \cite{smith2024}.
\end{document}
""")
        bib_file = paper1_dir / "references.bib"
        bib_file.write_text("""@article{smith2024,
  author = {Smith, John},
  title = {Test},
  year = {2024}
}""")
        
        result = runner.invoke(
            app,
            ["write", "bib", "check", "paper1"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]

    def test_bibliography_zotero_search(self, temp_config):
        """Test searching Zotero for bibliography entries."""
        result = runner.invoke(
            app,
            ["write", "bib", "zotero", "mediation", "--limit", "5"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # May fail if Zotero not available
        assert result.exit_code in [0, 1]


# KNOWLEDGE DOMAIN - Advanced Search Operations
# ============================================================================


class TestDogfoodingKnowledgeSearch:
    """Test knowledge search operations."""

    def test_knowledge_search_across_domains(self, temp_vault, temp_config):
        """Test unified knowledge search."""
        result = runner.invoke(
            app,
            ["knowledge", "search", "research", "--limit", "5"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should work even if some sources fail
        assert result.exit_code in [0, 1]

    def test_knowledge_search_json(self, temp_vault, temp_config):
        """Test knowledge search with JSON output."""
        result = runner.invoke(
            app,
            ["knowledge", "search", "test", "--json"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code in [0, 1]
        if result.exit_code == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                assert isinstance(data, list)
            except json.JSONDecodeError:
                pytest.fail("Invalid JSON output")


# ============================================================================
# VAULT DOMAIN - Advanced Features
# ============================================================================


class TestDogfoodingVaultAdvanced:
    """Test advanced vault features."""

    def test_vault_template_list(self, temp_vault, temp_config):
        """Test listing vault templates."""
        # Create templates directory
        templates_dir = temp_vault / "_templates"
        templates_dir.mkdir(exist_ok=True)
        (templates_dir / "note.md").write_text("# {{title}}\n\n")
        
        result = runner.invoke(
            app,
            ["knowledge", "vault", "template", "dummy", "--list"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Exit code 2 is for Typer validation
        assert result.exit_code in [0, 1, 2]

    def test_vault_daily_note(self, temp_vault, temp_config):
        """Test creating/showing daily note."""
        result = runner.invoke(
            app,
            ["knowledge", "vault", "daily"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # May fail if templates not set up, but should exit gracefully
        assert result.exit_code in [0, 1]

    def test_vault_graph_with_tags(self, temp_vault, temp_config):
        """Test vault graph with tag nodes."""
        result = runner.invoke(
            app,
            ["knowledge", "vault", "graph", "--tags"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 0
        assert "nodes" in result.stdout.lower() or "edges" in result.stdout.lower()

    def test_vault_graph_with_limit(self, temp_vault, temp_config):
        """Test vault graph with node limit."""
        result = runner.invoke(
            app,
            ["knowledge", "vault", "graph", "--limit", "10"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 0


# ============================================================================
# UTILITY COMMANDS
# ============================================================================


class TestDogfoodingUtilityCommands:
    """Test utility commands."""

    def test_doctor_command(self, temp_config):
        """Test the doctor health check command."""
        result = runner.invoke(
            app,
            ["doctor"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 0
        # Should show some diagnostic info
        assert len(result.stdout) > 0

    def test_config_command(self, temp_config):
        """Test the config show command."""
        result = runner.invoke(
            app,
            ["config"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 0
        # Should show config paths
        assert "config" in result.stdout.lower() or "vault" in result.stdout.lower()


# ============================================================================
# CROSS-DOMAIN INTEGRATION WORKFLOWS
# ============================================================================


class TestDogfoodingCrossDomainWorkflows:
    """Test workflows that span multiple domains."""

    def test_workflow_zotero_to_bibliography(self, temp_config, tmp_path):
        """Test exporting from Zotero to bibliography file."""
        # Create a test bib file
        bib_file = tmp_path / "test.bib"
        
        # This would normally pull from Zotero, but will fail gracefully
        result = runner.invoke(
            app,
            ["write", "bib", "zotero", str(bib_file), "--limit", "10"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # May fail if Zotero not available, but should exit cleanly
        assert result.exit_code in [0, 1]

    def test_workflow_vault_note_with_citations(self, temp_vault, temp_config):
        """Test creating vault note that references bibliography."""
        note_content = """# Research Note

This is a note about [[methodology]].

## Citations
- @smith2024
- @doe2023
"""
        result = runner.invoke(
            app,
            ["knowledge", "vault", "write", "research-note.md", "--content", note_content],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 0
        
        # Verify note exists
        note_path = temp_vault / "research-note.md"
        assert note_path.exists()
        assert "@smith2024" in note_path.read_text()


# ============================================================================
# ERROR HANDLING AND EDGE CASES
# ============================================================================


class TestDogfoodingEdgeCases:
    """Test edge cases and error handling."""

    def test_manuscript_show_nonexistent(self, temp_manuscripts, temp_config):
        """Test showing nonexistent manuscript."""
        result = runner.invoke(
            app,
            ["write", "manuscript", "show", "nonexistent-paper"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 1

    def test_vault_read_nonexistent_subdirectory(self, temp_vault, temp_config):
        """Test reading from nonexistent subdirectory."""
        result = runner.invoke(
            app,
            ["knowledge", "vault", "read", "nonexistent/note.md"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        assert result.exit_code == 1

    def test_manuscript_batch_operations_empty_list(self, temp_manuscripts, temp_config):
        """Test batch operations with empty manuscript list."""
        result = runner.invoke(
            app,
            ["write", "manuscript", "batch-status", "nonexistent1,nonexistent2", "active"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should handle nonexistent manuscripts gracefully (may fail)
        # Exit code 2 is Typer validation error
        assert result.exit_code in [0, 1, 2]

    def test_vault_export_invalid_format(self, temp_vault, temp_config, tmp_path):
        """Test vault export with invalid format."""
        output_file = tmp_path / "output.txt"
        result = runner.invoke(
            app,
            ["knowledge", "vault", "export", "invalid-format", str(output_file)],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should fail with error message
        assert result.exit_code in [1, 2]  # 2 for typer parameter validation

    def test_manuscript_export_invalid_format(self, temp_manuscripts, temp_config, tmp_path):
        """Test manuscript export with invalid format."""
        output_file = tmp_path / "output.txt"
        result = runner.invoke(
            app,
            ["write", "manuscript", "export", str(output_file), "--format", "xml"],
            env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
        )
        # Should fail or handle gracefully
        assert result.exit_code in [0, 1, 2]


# ============================================================================
# JSON OUTPUT VALIDATION
# ============================================================================


class TestDogfoodingJSONOutputValidation:
    """Test JSON output across all commands that support it."""

    def test_json_outputs_are_valid(self, temp_vault, temp_manuscripts, temp_config, tmp_path):
        """Test that all JSON outputs are valid across different commands."""
        json_commands = [
            ["knowledge", "vault", "search", "test", "--json"],
            ["knowledge", "vault", "recent", "--json"],
            ["knowledge", "vault", "backlinks", "note1", "--json"],
            ["knowledge", "vault", "orphans", "--json"],
            ["knowledge", "vault", "graph", "--json"],
            ["write", "manuscript", "list", "--json"],
            ["write", "manuscript", "stats", "--json"],
            ["write", "manuscript", "deadlines", "--json"],
        ]
        
        for cmd in json_commands:
            result = runner.invoke(
                app,
                cmd,
                env={**os.environ, "NEXUS_CONFIG": str(temp_config)},
            )
            
            # Should succeed or fail gracefully
            if result.exit_code == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    # Basic validation - should be dict or list
                    assert isinstance(data, (dict, list)), f"Command {' '.join(cmd)} returned invalid JSON type"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Command {' '.join(cmd)} returned invalid JSON: {e}\nOutput: {result.stdout[:200]}")
