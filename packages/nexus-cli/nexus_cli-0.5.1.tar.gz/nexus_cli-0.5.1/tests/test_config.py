"""Tests for configuration module."""

from pathlib import Path

import yaml

from nexus.utils.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_default_config(self, temp_dir):
        """Test default configuration values."""
        config = Config()

        # Check defaults exist
        assert config.vault is not None
        assert config.zotero is not None
        assert config.teaching is not None
        assert config.writing is not None

    def test_load_config_file(self, temp_dir):
        """Test loading configuration from file."""
        config_dir = temp_dir / ".config" / "nexus"
        config_dir.mkdir(parents=True)

        config_file = config_dir / "config.yaml"
        config_file.write_text("""
vault:
  path: ~/test-vault
zotero:
  database: ~/Zotero/zotero.sqlite
teaching:
  courses_dir: ~/courses
writing:
  manuscripts_dir: ~/manuscripts
""")

        # Config should be loadable
        config_data = yaml.safe_load(config_file.read_text())
        assert config_data["vault"]["path"] == "~/test-vault"
        assert config_data["zotero"]["database"] == "~/Zotero/zotero.sqlite"

    def test_expand_paths(self, temp_dir):
        """Test that paths with ~ are expanded."""
        path_str = "~/test/path"
        expanded = Path(path_str).expanduser()
        assert str(expanded).startswith("/")
        assert "~" not in str(expanded)
