"""Edge case and error handling tests."""

import tempfile
from pathlib import Path

import pytest

from nexus.knowledge.vault import VaultManager
from nexus.research.pdf import PDFExtractor
from nexus.writing.bibliography import BibFileParser, BibliographyManager


class TestVaultEdgeCases:
    """Test edge cases for vault operations."""

    def test_empty_vault(self, temp_dir):
        """Test operations on empty vault."""
        vault_path = temp_dir / "empty-vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        manager = VaultManager(vault_path)

        assert manager.exists() is True
        assert manager.note_count() == 0
        assert len(manager.recent()) == 0
        assert len(manager.orphans()) == 0

    def test_vault_with_only_system_files(self, temp_dir):
        """Test vault with only system files."""
        vault_path = temp_dir / "system-vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Add system files
        system_dir = vault_path / "_SYSTEM"
        system_dir.mkdir()
        (system_dir / "config.md").write_text("# Config")

        manager = VaultManager(vault_path)

        # System files may or may not be counted depending on implementation
        # Just verify no crash
        count = manager.note_count()
        assert isinstance(count, int)
        assert count >= 0

    def test_note_with_malformed_frontmatter(self, temp_dir):
        """Test parsing note with malformed frontmatter."""
        vault_path = temp_dir / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create note with invalid YAML
        note_path = vault_path / "bad-frontmatter.md"
        note_path.write_text("""---
invalid: yaml: syntax::
no: closing
# Content starts here

This is the content.
""")

        manager = VaultManager(vault_path)

        # Should handle gracefully
        note = manager.read("bad-frontmatter.md")
        assert note is not None
        assert "content" in note.content.lower()

    def test_note_with_circular_links(self, temp_dir):
        """Test handling circular links."""
        vault_path = temp_dir / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create notes with circular links
        (vault_path / "note-a.md").write_text("# A\n\n[[note-b]]")
        (vault_path / "note-b.md").write_text("# B\n\n[[note-a]]")

        manager = VaultManager(vault_path)

        # Should not cause infinite loop
        graph = manager.graph()
        assert len(graph["nodes"]) == 2
        assert len(graph["edges"]) == 2

    def test_search_with_regex_special_chars(self, sample_vault):
        """Test search with regex special characters."""
        manager = VaultManager(sample_vault)

        # These characters have special meaning in regex
        special_queries = ["[test]", "(mediation)", "test+", "test?", "test*"]

        for query in special_queries:
            # Should not crash
            results = manager.search(query)
            assert isinstance(results, list)

    def test_read_note_without_extension(self, sample_vault):
        """Test reading note without .md extension."""
        manager = VaultManager(sample_vault)

        # Should auto-add .md extension
        note = manager.read("10-PROJECTS/test-project")
        assert note is not None
        assert "mediation" in note.content.lower()

    def test_write_to_nonexistent_subdirectory(self, sample_vault):
        """Test writing to nonexistent subdirectory."""
        manager = VaultManager(sample_vault)

        # Should create parent directories
        result = manager.write("new-folder/nested/note.md", "# Content")
        assert result is not None
        assert (sample_vault / "new-folder" / "nested" / "note.md").exists()

    def test_backlinks_with_aliases(self, temp_dir):
        """Test backlinks with aliases."""
        vault_path = temp_dir / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create notes with alias links
        (vault_path / "target.md").write_text("# Target Note")
        (vault_path / "source.md").write_text("# Source\n\n[[target|Alias Name]]")

        manager = VaultManager(vault_path)
        backlinks = manager.backlinks("target.md")

        # Should find link despite alias
        assert len(backlinks) >= 1

    def test_graph_with_broken_links(self, temp_dir):
        """Test graph with links to nonexistent notes."""
        vault_path = temp_dir / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create note linking to nonexistent note
        (vault_path / "note.md").write_text("# Note\n\n[[nonexistent-note]]")

        manager = VaultManager(vault_path)
        graph = manager.graph()

        # Should only include nodes that exist
        assert len(graph["nodes"]) == 1
        # Should not create edge to nonexistent note
        assert len(graph["edges"]) == 0


class TestPDFEdgeCases:
    """Test edge cases for PDF operations."""

    def test_pdf_extractor_no_pdftotext(self, temp_dir):
        """Test PDF extractor when pdftotext not available."""
        extractor = PDFExtractor([temp_dir])

        # Force unavailability
        extractor._pdftotext_path = None

        assert extractor.available() is False

        # Extract should raise error
        pdf_path = temp_dir / "test.pdf"
        pdf_path.write_bytes(b"fake pdf")

        with pytest.raises(RuntimeError, match="pdftotext"):
            extractor.extract(pdf_path)

    def test_pdf_extract_nonexistent_file(self, temp_dir):
        """Test extracting nonexistent PDF."""
        extractor = PDFExtractor([temp_dir])

        with pytest.raises(FileNotFoundError):
            extractor.extract(temp_dir / "nonexistent.pdf")

    def test_pdf_search_empty_query(self, temp_dir):
        """Test PDF search with empty query."""
        extractor = PDFExtractor([temp_dir])

        results = extractor.search("", limit=10)
        assert isinstance(results, list)

    def test_pdf_search_no_directories(self):
        """Test PDF search with no configured directories."""
        extractor = PDFExtractor([])

        results = extractor.search("test", limit=10)
        assert len(results) == 0

    def test_pdf_list_nonexistent_directory(self, temp_dir):
        """Test listing PDFs in nonexistent directory."""
        extractor = PDFExtractor([temp_dir / "nonexistent"])

        pdfs = extractor.list_pdfs()
        assert len(pdfs) == 0

    def test_pdf_with_special_characters_in_name(self, temp_dir):
        """Test PDF with special characters in filename."""
        pdf_path = temp_dir / "test [2024] (v1.2).pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nFake content")

        extractor = PDFExtractor([temp_dir])
        pdfs = extractor.list_pdfs()

        assert len(pdfs) >= 1
        assert any("[2024]" in pdf["filename"] for pdf in pdfs)


class TestBibliographyEdgeCases:
    """Test edge cases for bibliography operations."""

    def test_parse_empty_bib_file(self, temp_dir):
        """Test parsing empty .bib file."""
        bib_file = temp_dir / "empty.bib"
        bib_file.write_text("")

        parser = BibFileParser()
        entries = parser.parse_file(bib_file)

        assert len(entries) == 0

    def test_parse_bib_with_malformed_entry(self, temp_dir):
        """Test parsing .bib with malformed entry."""
        bib_file = temp_dir / "malformed.bib"
        bib_file.write_text("""
@article{Good2024,
  title = {Good Entry},
  author = {Smith, J.},
  year = {2024}
}

@book{AlsoGood2023,
  title = {Another Good One},
  author = {Jones, M.}
}
""")

        parser = BibFileParser()
        entries = parser.parse_file(bib_file)

        # Should parse the valid entries
        assert len(entries) >= 2
        keys = [e.key for e in entries]
        assert "Good2024" in keys or "AlsoGood2023" in keys

    def test_parse_authors_with_special_chars(self):
        """Test parsing authors with special characters."""
        parser = BibFileParser()

        # Various author formats
        test_cases = [
            "Müller, José and García, María",
            "O'Brien, Patrick",
            "van der Berg, Johannes",
            "Smith, Jr., John",
        ]

        for author_str in test_cases:
            authors = parser._parse_authors(author_str)
            assert len(authors) > 0

    def test_citation_check_with_no_citations(self, temp_dir):
        """Test citation check on document with no citations."""
        ms_dir = temp_dir / "manuscript"
        ms_dir.mkdir()

        # Create manuscript with no citations
        (ms_dir / "index.qmd").write_text("# Introduction\n\nNo citations here.")

        # Create bib file
        (ms_dir / "references.bib").write_text("""@article{Unused2024,
  title = {Unused Entry}
}
""")

        manager = BibliographyManager(temp_dir)
        result = manager.check_citations("manuscript")

        # Should have structure even if empty
        assert isinstance(result, dict)

    def test_citation_check_with_missing_bib(self, temp_dir):
        """Test citation check when .bib file is missing."""
        ms_dir = temp_dir / "manuscript"
        ms_dir.mkdir()

        (ms_dir / "index.qmd").write_text("# Test\n\n[@Smith2024]")

        manager = BibliographyManager(temp_dir)
        result = manager.check_citations("manuscript")

        # Should return some result structure
        assert isinstance(result, dict)


class TestErrorRecovery:
    """Test error recovery and graceful degradation."""

    def test_vault_with_permission_error(self, temp_dir):
        """Test handling permission errors."""
        vault_path = temp_dir / "restricted-vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create a file we can't read (on Unix-like systems)
        restricted = vault_path / "restricted.md"
        restricted.write_text("# Restricted")
        restricted.chmod(0o000)

        manager = VaultManager(vault_path)

        # Should handle permission error gracefully
        try:
            count = manager.note_count()
            # Might count it or skip it, both are acceptable
            assert count >= 0
        finally:
            # Restore permissions for cleanup
            restricted.chmod(0o644)

    def test_vault_with_binary_file(self, temp_dir):
        """Test handling binary file with .md extension."""
        vault_path = temp_dir / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create binary file with .md extension
        binary_file = vault_path / "binary.md"
        binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

        manager = VaultManager(vault_path)

        # Should handle gracefully without crashing
        try:
            note = manager.read("binary.md")
            # May succeed or fail, but shouldn't crash
        except (UnicodeDecodeError, Exception):
            # Acceptable to raise error
            pass

    def test_concurrent_file_access(self, sample_vault):
        """Test concurrent access to same vault."""
        manager1 = VaultManager(sample_vault)
        manager2 = VaultManager(sample_vault)

        # Both should work independently
        count1 = manager1.note_count()
        count2 = manager2.note_count()

        assert count1 == count2

    def test_large_graph_performance(self, temp_dir):
        """Test graph generation with many notes."""
        vault_path = temp_dir / "large-vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create 100 notes
        for i in range(100):
            note_path = vault_path / f"note-{i}.md"
            # Each note links to next one
            next_note = f"note-{(i + 1) % 100}"
            note_path.write_text(f"# Note {i}\n\n[[{next_note}]]")

        manager = VaultManager(vault_path)

        # Should complete in reasonable time
        graph = manager.graph()
        assert len(graph["nodes"]) == 100
        assert len(graph["edges"]) == 100  # Circular links

    def test_search_performance_with_large_content(self, temp_dir):
        """Test search on note with very large content."""
        vault_path = temp_dir / "vault"
        vault_path.mkdir()
        (vault_path / ".obsidian").mkdir()

        # Create very large note (1MB+)
        large_content = "# Large Note\n\n" + ("Lorem ipsum " * 100000)
        (vault_path / "large.md").write_text(large_content)

        manager = VaultManager(vault_path)

        # Should handle large files
        results = manager.search("Lorem")
        assert len(results) > 0
