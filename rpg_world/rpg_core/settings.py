"""RPG World settings — shared by core and API layers.

Settings are read from ``rpg_world/settings.json``.  Relative paths
in the file are resolved against the ``rpg_world/`` package root.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Location of settings.json relative to this module
_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "settings.json"
# Package root used to resolve relative paths
_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _load() -> dict[str, Any]:
    if _SETTINGS_PATH.is_file():
        with _SETTINGS_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def _resolve(value: str) -> str:
    """Resolve a path — return as-is if absolute, else relative to package root."""
    p = Path(value)
    return str(p if p.is_absolute() else _PACKAGE_ROOT / p)


class Settings:
    """Read-only settings proxy.  Attributes mirror keys in settings.json."""

    def __init__(self) -> None:
        self._raw = _load()

    @property
    def character_path(self) -> str:
        return _resolve(self._raw.get("character_path", "data/character"))

    @property
    def lorebook_path(self) -> str:
        return _resolve(self._raw.get("lorebook_path", "data/lorebook"))


# Singleton
settings = Settings()
