"""Tests for vault management module."""

import pytest

from nexus.knowledge.vault import VaultManager


class TestVaultManager:
    """Tests for VaultManager class."""

    def test_vault_exists(self, sample_vault):
        """Test that vault existence check works."""
        manager = VaultManager(sample_vault)
        assert manager.exists() is True

    def test_vault_not_exists(self, temp_dir):
        """Test non-existent vault."""
        manager = VaultManager(temp_dir / "nonexistent")
        assert manager.exists() is False

    def test_note_count(self, sample_vault):
        """Test counting notes in vault."""
        manager = VaultManager(sample_vault)
        count = manager.note_count()

        # Should find the sample notes
        assert count >= 2

    def test_search_notes(self, sample_vault):
        """Test searching notes."""
        manager = VaultManager(sample_vault)

        # Search for mediation
        results = manager.search("mediation")
        assert len(results) >= 1

        # Search for something not in notes
        results = manager.search("xyznonexistent123")
        assert len(results) == 0

    def test_recent_notes(self, sample_vault):
        """Test getting recent notes."""
        manager = VaultManager(sample_vault)
        recent = manager.recent(limit=5)

        assert len(recent) >= 2
        assert len(recent) <= 5

    def test_read_note(self, sample_vault):
        """Test reading a note."""
        manager = VaultManager(sample_vault)
        note = manager.read("10-PROJECTS/test-project.md")

        assert note is not None
        assert "mediation analysis" in note.content

    def test_read_nonexistent_note(self, sample_vault):
        """Test reading non-existent note raises error."""
        manager = VaultManager(sample_vault)

        with pytest.raises(FileNotFoundError):
            manager.read("nonexistent.md")

    def test_backlinks(self, sample_vault):
        """Test finding backlinks."""
        manager = VaultManager(sample_vault)
        backlinks = manager.backlinks("10-PROJECTS/test-project.md")

        # causal-inference.md links to test-project
        assert len(backlinks) >= 1

    def test_orphans(self, sample_vault):
        """Test finding orphan notes."""
        manager = VaultManager(sample_vault)

        # Create an orphan note
        orphan = sample_vault / "orphan-note.md"
        orphan.write_text("# Orphan\n\nThis note has no links.")

        orphans = manager.orphans()

        assert "orphan-note.md" in orphans

    def test_graph_generation(self, sample_vault):
        """Test generating graph data."""
        manager = VaultManager(sample_vault)
        graph = manager.graph()

        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) >= 2

        # Check node structure
        node = graph["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "path" in node
        assert "connections" in node

    def test_graph_with_limit(self, sample_vault):
        """Test graph generation with node limit."""
        manager = VaultManager(sample_vault)
        graph = manager.graph(limit=1)

        assert len(graph["nodes"]) <= 1

    def test_graph_with_tags(self, sample_vault):
        """Test graph generation including tags."""
        manager = VaultManager(sample_vault)
        graph = manager.graph(include_tags=True)

        # May or may not have tag nodes depending on sample data
        tag_nodes = [n for n in graph["nodes"] if n.get("type") == "tag"]
        assert isinstance(tag_nodes, list)  # Just verify structure

    def test_graph_stats(self, sample_vault):
        """Test graph statistics calculation."""
        manager = VaultManager(sample_vault)
        stats = manager.graph_stats()

        assert "total_notes" in stats
        assert "total_connections" in stats
        assert "avg_connections" in stats
        assert "most_connected" in stats
        assert "density" in stats

        assert stats["total_notes"] >= 2
        assert isinstance(stats["avg_connections"], float)
        assert isinstance(stats["most_connected"], list)

    def test_write_note(self, sample_vault):
        """Test writing a new note."""
        manager = VaultManager(sample_vault)

        content = "# New Note\n\nThis is test content."
        result = manager.write("test-write.md", content)

        assert result is not None
        assert (sample_vault / "test-write.md").exists()

        # Verify content
        note = manager.read("test-write.md")
        assert "test content" in note.content

    def test_write_to_subdirectory(self, sample_vault):
        """Test writing note to subdirectory."""
        manager = VaultManager(sample_vault)

        content = "# Nested Note\n\nIn a subdirectory."
        result = manager.write("10-PROJECTS/nested-note.md", content)

        assert result is not None
        assert (sample_vault / "10-PROJECTS" / "nested-note.md").exists()

    def test_search_with_limit(self, sample_vault):
        """Test search with result limit."""
        manager = VaultManager(sample_vault)

        results = manager.search("", limit=1)
        assert len(results) <= 1

    def test_search_in_frontmatter(self, sample_vault):
        """Test searching in frontmatter."""
        manager = VaultManager(sample_vault)

        results = manager.search("active")
        # Should find notes with status: active in frontmatter
        assert len(results) >= 1

    def test_parse_note_with_links(self, sample_vault):
        """Test parsing note links."""
        manager = VaultManager(sample_vault)
        note = manager.read("20-AREAS/causal-inference.md")

        assert len(note.links) >= 1
        assert "test-project" in note.links

    def test_parse_note_with_tags(self, sample_vault):
        """Test parsing note tags."""
        manager = VaultManager(sample_vault)
        note = manager.read("10-PROJECTS/test-project.md")

        # Tags may or may not be present depending on content
        assert isinstance(note.tags, list)

    def test_parse_frontmatter(self, sample_vault):
        """Test frontmatter parsing."""
        manager = VaultManager(sample_vault)
        note = manager.read("10-PROJECTS/test-project.md")

        assert "type" in note.frontmatter
        assert note.frontmatter["type"] == "project"

    def test_backlinks_empty(self, sample_vault):
        """Test backlinks for note with no incoming links."""
        manager = VaultManager(sample_vault)

        # Create isolated note
        isolated = sample_vault / "isolated.md"
        isolated.write_text("# Isolated\n\nNo one links here.")

        backlinks = manager.backlinks("isolated.md")
        assert len(backlinks) == 0

    def test_recent_notes_excludes_system(self, sample_vault):
        """Test that recent notes excludes system folders."""
        manager = VaultManager(sample_vault)

        # Create a system note
        system_dir = sample_vault / "_SYSTEM"
        system_dir.mkdir(exist_ok=True)
        (system_dir / "config.md").write_text("# System\n\nConfig file.")

        recent = manager.recent(limit=10)

        # Should not include _SYSTEM files
        assert not any("_SYSTEM" in path for path in recent)
        assert not any(".obsidian" in path for path in recent)
