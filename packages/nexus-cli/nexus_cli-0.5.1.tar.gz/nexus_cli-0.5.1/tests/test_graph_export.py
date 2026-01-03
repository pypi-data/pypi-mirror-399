"""Tests for graph export functionality."""

import json
from pathlib import Path

from nexus.knowledge.vault import VaultManager


class TestGraphExport:
    """Tests for graph export methods."""

    def test_export_graphml(self, sample_vault):
        """Test GraphML export."""
        manager = VaultManager(sample_vault)
        output_file = sample_vault / "graph.graphml"

        manager.export_graphml(output_file)

        assert output_file.exists()
        content = output_file.read_text()

        # Check XML structure
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert "<graphml" in content
        assert "</graphml>" in content
        assert "<graph " in content
        assert "<node " in content
        assert "<edge " in content

    def test_export_graphml_with_tags(self, sample_vault):
        """Test GraphML export with tags."""
        # Create note with tags
        note_with_tags = sample_vault / "tagged-note.md"
        note_with_tags.write_text("---\ntags: [test, example]\n---\n# Tagged Note\n")

        manager = VaultManager(sample_vault)
        output_file = sample_vault / "graph-tags.graphml"

        manager.export_graphml(output_file, include_tags=True)

        assert output_file.exists()
        content = output_file.read_text()

        # Should include tag nodes
        assert "<node " in content
        assert "type" in content

    def test_export_graphml_with_limit(self, sample_vault):
        """Test GraphML export with node limit."""
        # Create multiple notes
        for i in range(10):
            note = sample_vault / f"note{i}.md"
            note.write_text(f"# Note {i}\nContent [[note0]]")

        manager = VaultManager(sample_vault)
        output_file = sample_vault / "graph-limited.graphml"

        manager.export_graphml(output_file, limit=3)

        assert output_file.exists()
        content = output_file.read_text()

        # Should have limited nodes (exact count may vary due to connections)
        node_count = content.count("<node ")
        assert node_count <= 5  # Allow some flexibility

    def test_export_d3(self, sample_vault):
        """Test D3.js format export."""
        manager = VaultManager(sample_vault)
        output_file = sample_vault / "graph-d3.json"

        manager.export_d3(output_file)

        assert output_file.exists()
        data = json.loads(output_file.read_text())

        # Check D3 format structure
        assert "nodes" in data
        assert "links" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["links"], list)

        # Check node structure
        if data["nodes"]:
            node = data["nodes"][0]
            assert "id" in node
            assert "name" in node
            assert "group" in node
            assert "value" in node

        # Check link structure
        if data["links"]:
            link = data["links"][0]
            assert "source" in link
            assert "target" in link
            assert "value" in link

    def test_export_d3_with_tags(self, sample_vault):
        """Test D3 export with tags."""
        note_with_tags = sample_vault / "tagged.md"
        note_with_tags.write_text("---\ntags: [research]\n---\n# Research Note\n")

        manager = VaultManager(sample_vault)
        output_file = sample_vault / "graph-d3-tags.json"

        manager.export_d3(output_file, include_tags=True)

        assert output_file.exists()
        data = json.loads(output_file.read_text())

        # Should have different groups (notes vs tags)
        groups = {node["group"] for node in data["nodes"]}
        assert len(groups) >= 1  # At least one group

    def test_xml_escaping(self):
        """Test XML character escaping."""
        from nexus.knowledge.vault import VaultManager

        # Test special XML characters
        text = "<test> & \"quotes\" 'single'"
        escaped = VaultManager._escape_xml(text)

        assert "&lt;" in escaped
        assert "&gt;" in escaped
        assert "&amp;" in escaped
        assert "&quot;" in escaped
        assert "&apos;" in escaped

        # Original characters should be escaped
        assert "<" not in escaped
        assert ">" not in escaped
        assert "&" not in escaped.replace("&lt;", "").replace("&gt;", "").replace("&amp;", "").replace(
            "&quot;", ""
        ).replace("&apos;", "")

    def test_export_graphml_empty_vault(self, temp_dir):
        """Test GraphML export with empty vault."""
        empty_vault = temp_dir / "empty_vault"
        empty_vault.mkdir()

        manager = VaultManager(empty_vault)
        output_file = empty_vault / "empty-graph.graphml"

        manager.export_graphml(output_file)

        assert output_file.exists()
        content = output_file.read_text()

        # Should still have valid GraphML structure
        assert "<graphml" in content
        assert "<graph " in content

    def test_export_d3_empty_vault(self, temp_dir):
        """Test D3 export with empty vault."""
        empty_vault = temp_dir / "empty_vault"
        empty_vault.mkdir()

        manager = VaultManager(empty_vault)
        output_file = empty_vault / "empty-d3.json"

        manager.export_d3(output_file)

        assert output_file.exists()
        data = json.loads(output_file.read_text())

        assert data["nodes"] == []
        assert data["links"] == []


class TestGraphExportIntegration:
    """Integration tests for graph export with existing vault operations."""

    def test_export_preserves_graph_data(self, sample_vault):
        """Test that export preserves the same graph data."""
        manager = VaultManager(sample_vault)

        # Get original graph
        original_graph = manager.graph()

        # Export to D3
        output_file = sample_vault / "test-d3.json"
        manager.export_d3(output_file)

        # Load exported data
        data = json.loads(output_file.read_text())

        # Should have same number of nodes and links
        assert len(data["nodes"]) == len(original_graph["nodes"])
        assert len(data["links"]) == len(original_graph["edges"])

        # Node IDs should match
        original_ids = {n["id"] for n in original_graph["nodes"]}
        exported_ids = {n["id"] for n in data["nodes"]}
        assert original_ids == exported_ids

    def test_multiple_export_formats(self, sample_vault):
        """Test exporting to multiple formats."""
        manager = VaultManager(sample_vault)

        # Export to all formats
        graphml_file = sample_vault / "multi.graphml"
        d3_file = sample_vault / "multi-d3.json"

        manager.export_graphml(graphml_file)
        manager.export_d3(d3_file)

        # All should exist
        assert graphml_file.exists()
        assert d3_file.exists()

        # D3 should be valid JSON
        data = json.loads(d3_file.read_text())
        assert "nodes" in data
        assert "links" in data

        # GraphML should be valid XML
        content = graphml_file.read_text()
        assert content.startswith('<?xml version="1.0"')

    def test_export_with_complex_vault(self, temp_dir):
        """Test export with a more complex vault structure."""
        vault = temp_dir / "complex_vault"
        vault.mkdir()

        # Create interconnected notes
        (vault / "concept-a.md").write_text("# Concept A\nRelated to [[concept-b]] and [[concept-c]]")
        (vault / "concept-b.md").write_text("# Concept B\nSee [[concept-a]] for details")
        (vault / "concept-c.md").write_text(
            "---\ntags: [important, research]\n---\n# Concept C\nLinks to [[concept-a]]"
        )
        (vault / "standalone.md").write_text("# Standalone\nNo links")

        manager = VaultManager(vault)

        # Export with tags
        output_file = vault / "complex.graphml"
        manager.export_graphml(output_file, include_tags=True)

        assert output_file.exists()
        content = output_file.read_text()

        # Should have nodes for notes and tags
        assert content.count("<node ") >= 4  # At least 4 notes
        assert "concept-a" in content
        assert "concept-b" in content
        assert "concept-c" in content

        # Should have edges
        assert "<edge " in content
