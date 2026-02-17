"""Service configuration loaded from YAML file and environment variables.

Config layering (last wins):
  1. YAML file (base defaults for Docker)
  2. Environment variables (Compose wiring and overrides)
  3. CLI flags (handled by __init__.py, not here)

If no CONFIG_FILE env var is set, all values use hardcoded defaults
so local development works unchanged.
"""

from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    """gh-issues-local service configuration."""

    data_dir: Path = field(default_factory=lambda: Path.home())
    storage: dict[str, Any] | None = None
    auth_token: str | None = None


def load_config() -> Config:
    """Load configuration from YAML file (if set) then overlay env vars.

    Reads the ``CONFIG_FILE`` env var. If it points to a valid YAML file,
    that file provides base values. Env vars override YAML values.
    If ``CONFIG_FILE`` is unset or the file doesn't exist, defaults apply.

    Raises:
        ValueError: If the config file exists but contains malformed YAML.
    """
    raw: dict[str, Any] = {}
    config_path = os.environ.get("CONFIG_FILE")

    if config_path:
        path = Path(config_path)
        if path.is_file():
            try:
                with path.open() as f:
                    loaded = yaml.safe_load(f)
                if isinstance(loaded, dict):
                    raw = loaded
            except yaml.YAMLError as e:
                msg = f"Malformed YAML in config file {config_path}: {e}"
                raise ValueError(msg) from None
        else:
            logger.warning("CONFIG_FILE set to %s but file not found; using defaults", config_path)

    # --- Extract values from YAML ---
    storage = raw.get("storage")
    auth_section = raw.get("auth") or {}
    auth_token = auth_section.get("token")

    # --- Env var overrides ---
    data_dir_str = os.environ.get("GH_ISSUES_LOCAL_DATA_DIR", str(Path.home()))
    data_dir = Path(data_dir_str)

    return Config(
        data_dir=data_dir,
        storage=storage,
        auth_token=auth_token,
    )
