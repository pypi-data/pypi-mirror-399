"""
Configuration management for cdd-flow.
"""

from pathlib import Path

import yaml


def get_global_config() -> dict:
    """Load global configuration from ~/.cdd-flow/config.yaml"""
    config_path = Path("~/.cdd-flow/config.yaml").expanduser()
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_project_config(project_dir: Path | None = None) -> dict:
    """Load project-specific configuration."""
    if project_dir is None:
        project_dir = Path.cwd()
    
    config_path = Path(project_dir) / ".cdd-flow" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f) or {}
    return {}


def get_config(project_dir: Path | str | None = None) -> dict:
    """
    Get merged configuration (global + project).
    
    Project config overrides global config.
    """
    if project_dir is not None:
        project_dir = Path(project_dir)
    
    config = {
        # Defaults
        "landing_zone": "~/Downloads",
        "trash_dir": "~/.cdd-flow/trash",
        "trash_retention_days": 7,
        "default_recency_minutes": 15,
        "artifact_extensions": [
            ".tar", ".tar.gz", ".tgz",
            ".py", ".yaml", ".yml", ".json",
            ".md", ".html", ".jsx", ".tsx", ".ts", ".css"
        ],
    }
    
    # Merge global
    config.update(get_global_config())
    
    # Merge project
    config.update(get_project_config(project_dir))
    
    return config


def save_project_config(project_dir: Path, config: dict) -> None:
    """Save project configuration."""
    config_dir = project_dir / ".cdd-flow"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = config_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)
