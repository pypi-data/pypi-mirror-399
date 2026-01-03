"""Configuration management for Nexus CLI."""

from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class ZoteroConfig(BaseModel):
    """Zotero configuration."""

    database: str = "~/Zotero/zotero.sqlite"
    storage: str = "~/Zotero/storage"


class VaultConfig(BaseModel):
    """Obsidian vault configuration."""

    path: str = "~/Obsidian/Nexus"
    templates: str = "~/Obsidian/Nexus/_SYSTEM/templates"


class PDFConfig(BaseModel):
    """PDF configuration."""

    directories: list[str] = [
        "~/Documents/Research/PDFs",
        "~/Documents/Teaching/PDFs",
    ]
    index: str = "~/.nexus/pdf-index.db"


class TeachingConfig(BaseModel):
    """Teaching configuration."""

    courses_dir: str = "~/projects/teaching"
    materials_dir: str = "~/Documents/Teaching"


class WritingConfig(BaseModel):
    """Writing configuration."""

    manuscripts_dir: str = "~/projects/research"
    templates_dir: str = "~/.nexus/templates"


class RConfig(BaseModel):
    """R configuration."""

    executable: str = "/usr/local/bin/R"
    packages_dir: str = "~/projects/r-packages"


class OutputConfig(BaseModel):
    """Output configuration."""

    format: str = "rich"  # rich, json, plain
    color: bool = True
    pager: bool = False


class IntegrationsConfig(BaseModel):
    """Integration configuration."""

    aiterm: bool = True
    obsidian: bool = True
    claude_plugin: bool = True


class Config(BaseSettings):
    """Main Nexus configuration."""

    zotero: ZoteroConfig = ZoteroConfig()
    vault: VaultConfig = VaultConfig()
    pdf: PDFConfig = PDFConfig()
    teaching: TeachingConfig = TeachingConfig()
    writing: WritingConfig = WritingConfig()
    r: RConfig = RConfig()
    output: OutputConfig = OutputConfig()
    integrations: IntegrationsConfig = IntegrationsConfig()

    class Config:
        env_prefix = "NEXUS_"


def get_config_path() -> Path:
    """Get the configuration file path."""
    return Path.home() / ".config" / "nexus" / "config.yaml"


def load_config_from_file(path: Path) -> dict:
    """Load configuration from a YAML file."""
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def get_config() -> Config:
    """Get the current configuration, merging defaults with file config."""
    config_path = get_config_path()
    file_config = load_config_from_file(config_path)

    # Create config with defaults, then update with file values
    config = Config()

    if file_config:
        # Update nested configs
        if "zotero" in file_config:
            config.zotero = ZoteroConfig(**file_config["zotero"])
        if "vault" in file_config:
            config.vault = VaultConfig(**file_config["vault"])
        if "pdf" in file_config:
            config.pdf = PDFConfig(**file_config["pdf"])
        if "teaching" in file_config:
            config.teaching = TeachingConfig(**file_config["teaching"])
        if "writing" in file_config:
            config.writing = WritingConfig(**file_config["writing"])
        if "r" in file_config:
            config.r = RConfig(**file_config["r"])
        if "output" in file_config:
            config.output = OutputConfig(**file_config["output"])
        if "integrations" in file_config:
            config.integrations = IntegrationsConfig(**file_config["integrations"])

    return config


def save_config(config: Config, path: Path | None = None) -> None:
    """Save configuration to file."""
    if path is None:
        path = get_config_path()

    path.parent.mkdir(parents=True, exist_ok=True)

    config_dict = {
        "zotero": config.zotero.model_dump(),
        "vault": config.vault.model_dump(),
        "pdf": config.pdf.model_dump(),
        "teaching": config.teaching.model_dump(),
        "writing": config.writing.model_dump(),
        "r": config.r.model_dump(),
        "output": config.output.model_dump(),
        "integrations": config.integrations.model_dump(),
    }

    with open(path, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


def init_config() -> Path:
    """Initialize default configuration file if it doesn't exist."""
    config_path = get_config_path()
    if not config_path.exists():
        save_config(Config())
    return config_path
