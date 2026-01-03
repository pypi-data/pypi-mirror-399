"""Tests for batch manuscript operations."""

import json
from pathlib import Path

from nexus.writing.manuscript import ManuscriptManager


class TestBatchStatusUpdate:
    """Tests for batch_update_status method."""

    def test_batch_update_status_success(self, temp_dir):
        """Test successful batch status update."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        # Create test manuscripts
        for name in ["paper1", "paper2", "paper3"]:
            ms_dir = manuscripts_dir / name
            ms_dir.mkdir()
            (ms_dir / ".STATUS").write_text(f"status: draft\nprogress: 0\n")

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_update_status(["paper1", "paper2"], "under_review")

        assert results["success"] == 2
        assert results["failed"] == 0

        # Verify status was updated
        for name in ["paper1", "paper2"]:
            status_file = manuscripts_dir / name / ".STATUS"
            content = status_file.read_text()
            assert "status: under_review" in content

    def test_batch_update_status_nonexistent(self, temp_dir):
        """Test batch update with nonexistent manuscript."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        (manuscripts_dir / "paper1").mkdir()
        (manuscripts_dir / "paper1" / ".STATUS").write_text("status: draft\n")

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_update_status(["paper1", "nonexistent"], "review")

        assert results["success"] == 1
        assert results["failed"] == 1
        assert len(results["errors"]) == 1
        assert "nonexistent" in results["errors"][0]

    def test_batch_update_status_creates_file(self, temp_dir):
        """Test batch update creates .STATUS if missing."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        ms_dir = manuscripts_dir / "paper1"
        ms_dir.mkdir()
        # No .STATUS file

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_update_status(["paper1"], "draft")

        assert results["success"] == 1

        # Verify .STATUS was created
        status_file = ms_dir / ".STATUS"
        assert status_file.exists()
        assert "status: draft" in status_file.read_text()


class TestBatchProgressUpdate:
    """Tests for batch_update_progress method."""

    def test_batch_update_progress(self, temp_dir):
        """Test batch progress update."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        for name in ["paper1", "paper2"]:
            ms_dir = manuscripts_dir / name
            ms_dir.mkdir()
            (ms_dir / ".STATUS").write_text(f"status: draft\nprogress: 0\n")

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_update_progress({"paper1": 50, "paper2": 75})

        assert results["success"] == 2
        assert results["failed"] == 0

        # Verify progress was updated
        assert "progress: 50" in (manuscripts_dir / "paper1" / ".STATUS").read_text()
        assert "progress: 75" in (manuscripts_dir / "paper2" / ".STATUS").read_text()

    def test_batch_update_progress_invalid_value(self, temp_dir):
        """Test batch progress with invalid values."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        ms_dir = manuscripts_dir / "paper1"
        ms_dir.mkdir()
        (ms_dir / ".STATUS").write_text("status: draft\nprogress: 0\n")

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_update_progress({"paper1": 150})  # Invalid: > 100

        assert results["success"] == 0
        assert results["failed"] == 1
        assert "invalid progress" in results["errors"][0].lower()

    def test_batch_update_progress_creates_file(self, temp_dir):
        """Test progress update creates .STATUS if missing."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        ms_dir = manuscripts_dir / "paper1"
        ms_dir.mkdir()

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_update_progress({"paper1": 25})

        assert results["success"] == 1

        status_file = ms_dir / ".STATUS"
        assert status_file.exists()
        assert "progress: 25" in status_file.read_text()


class TestBatchArchive:
    """Tests for batch_archive method."""

    def test_batch_archive(self, temp_dir):
        """Test batch archiving manuscripts."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        # Create manuscripts
        for name in ["old1", "old2"]:
            ms_dir = manuscripts_dir / name
            ms_dir.mkdir()
            (ms_dir / ".STATUS").write_text(f"status: complete\n")
            (ms_dir / "paper.tex").write_text("Content")

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_archive(["old1", "old2"])

        assert results["success"] == 2
        assert results["failed"] == 0

        # Verify manuscripts were moved
        archive_dir = manuscripts_dir / "Archive"
        assert archive_dir.exists()
        assert (archive_dir / "old1").exists()
        assert (archive_dir / "old2").exists()

        # Original locations should be gone
        assert not (manuscripts_dir / "old1").exists()
        assert not (manuscripts_dir / "old2").exists()

        # Status should be updated
        for name in ["old1", "old2"]:
            status_file = archive_dir / name / ".STATUS"
            content = status_file.read_text()
            assert "status: archived" in content

    def test_batch_archive_already_archived(self, temp_dir):
        """Test archiving manuscript that doesn't exist."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        archive_dir = manuscripts_dir / "Archive"
        archive_dir.mkdir()

        archived_ms = archive_dir / "already_archived"
        archived_ms.mkdir()

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_archive(["already_archived"])

        assert results["success"] == 0
        assert results["failed"] == 1
        assert "not found" in results["errors"][0].lower()

    def test_batch_archive_nonexistent(self, temp_dir):
        """Test archiving nonexistent manuscript."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_archive(["nonexistent"])

        assert results["success"] == 0
        assert results["failed"] == 1
        assert "not found" in results["errors"][0].lower()

    def test_batch_archive_preserves_files(self, temp_dir):
        """Test that archiving preserves all files."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        ms_dir = manuscripts_dir / "complete_paper"
        ms_dir.mkdir()
        (ms_dir / ".STATUS").write_text("status: complete\n")
        (ms_dir / "paper.tex").write_text("Content")
        (ms_dir / "refs.bib").write_text("@article{key}")
        (ms_dir / "figures").mkdir()
        (ms_dir / "figures" / "fig1.png").write_text("image")

        manager = ManuscriptManager(manuscripts_dir)
        results = manager.batch_archive(["complete_paper"])

        assert results["success"] == 1

        # Verify all files were moved
        archived = manuscripts_dir / "Archive" / "complete_paper"
        assert (archived / "paper.tex").exists()
        assert (archived / "refs.bib").exists()
        assert (archived / "figures" / "fig1.png").exists()


class TestBatchExportMetadata:
    """Tests for batch_export_metadata method."""

    def test_export_metadata_json(self, temp_dir):
        """Test exporting metadata to JSON."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        # Create manuscripts
        for i, name in enumerate(["paper1", "paper2"]):
            ms_dir = manuscripts_dir / name
            ms_dir.mkdir()
            (ms_dir / ".STATUS").write_text(f"status: draft\nprogress: {i * 25}\n")
            (ms_dir / "index.qmd").write_text("# Title\nContent")

        manager = ManuscriptManager(manuscripts_dir)
        output_file = temp_dir / "export.json"

        manager.batch_export_metadata(output_file, format="json")

        assert output_file.exists()
        data = json.loads(output_file.read_text())

        assert isinstance(data, list)
        assert len(data) >= 2

        # Check structure
        manuscript = data[0]
        assert "name" in manuscript
        assert "status" in manuscript
        assert "progress" in manuscript

    def test_export_metadata_csv(self, temp_dir):
        """Test exporting metadata to CSV."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        # Create manuscript
        ms_dir = manuscripts_dir / "paper1"
        ms_dir.mkdir()
        (ms_dir / ".STATUS").write_text("status: draft\nprogress: 50\n")
        (ms_dir / "index.qmd").write_text("# Title\nContent")

        manager = ManuscriptManager(manuscripts_dir)
        output_file = temp_dir / "export.csv"

        manager.batch_export_metadata(output_file, format="csv")

        assert output_file.exists()
        content = output_file.read_text()

        # Check CSV structure
        assert "name" in content
        assert "status" in content
        assert "progress" in content
        assert "paper1" in content
        assert "draft" in content

    def test_export_metadata_invalid_format(self, temp_dir):
        """Test export with invalid format."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        manager = ManuscriptManager(manuscripts_dir)
        output_file = temp_dir / "export.txt"

        try:
            manager.batch_export_metadata(output_file, format="invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Unsupported format" in str(e)

    def test_export_metadata_empty(self, temp_dir):
        """Test export with no manuscripts."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        manager = ManuscriptManager(manuscripts_dir)
        output_file = temp_dir / "empty.json"

        manager.batch_export_metadata(output_file, format="json")

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data == []


class TestBatchOperationsIntegration:
    """Integration tests for batch operations."""

    def test_workflow_update_and_archive(self, temp_dir):
        """Test workflow: update status, then archive."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        # Create manuscripts
        for name in ["completed1", "completed2", "draft1"]:
            ms_dir = manuscripts_dir / name
            ms_dir.mkdir()
            (ms_dir / ".STATUS").write_text("status: draft\nprogress: 0\n")

        manager = ManuscriptManager(manuscripts_dir)

        # Update completed ones
        results = manager.batch_update_status(["completed1", "completed2"], "complete")
        assert results["success"] == 2

        # Update progress
        results = manager.batch_update_progress({"completed1": 100, "completed2": 100})
        assert results["success"] == 2

        # Archive completed
        results = manager.batch_archive(["completed1", "completed2"])
        assert results["success"] == 2

        # Verify only draft1 remains
        active = [m.name for m in manager.list_manuscripts(include_archived=False)]
        assert "draft1" in active
        assert "completed1" not in active
        assert "completed2" not in active

    def test_export_after_updates(self, temp_dir):
        """Test exporting after batch updates."""
        manuscripts_dir = temp_dir / "manuscripts"
        manuscripts_dir.mkdir()

        for name in ["paper1", "paper2"]:
            ms_dir = manuscripts_dir / name
            ms_dir.mkdir()
            (ms_dir / ".STATUS").write_text("status: draft\n")

        manager = ManuscriptManager(manuscripts_dir)

        # Do batch updates
        manager.batch_update_status(["paper1"], "review")
        manager.batch_update_progress({"paper2": 75})

        # Export
        output_file = temp_dir / "updated.json"
        manager.batch_export_metadata(output_file)

        # Verify export reflects updates
        data = json.loads(output_file.read_text())

        paper1_data = next(m for m in data if m["name"] == "paper1")
        paper2_data = next(m for m in data if m["name"] == "paper2")

        assert paper1_data["status"] == "review"
        assert paper2_data["progress"] == 75
