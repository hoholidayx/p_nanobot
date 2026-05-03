"""CharacterLoader — load/save/delete individual character card files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rpg_world.rpg_core.utils import delete_file, load_json, save_json


def _slug(name: str) -> str:
    """Simple slug from character name — lower, replace spaces with ``_``."""
    return name.lower().replace(" ", "_")


class CharacterLoader:
    """File I/O for character cards stored as individual ``.json`` files.

    Directory layout::

        path/
        ├── alice.json
        ├── bob.json
        └── …
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def list_files(self) -> list[Path]:
        """Return sorted list of all ``.json`` files in the directory."""
        if not self.path.is_dir():
            return []
        return sorted(self.path.glob("*.json"))

    def load_all(self) -> list[dict[str, Any]]:
        """Load every character card from the directory.

        Returns a list of dicts (one per file).
        """
        characters: list[dict[str, Any]] = []
        for fpath in self.list_files():
            data = load_json(fpath)
            if isinstance(data, dict):
                characters.append(data)
            elif isinstance(data, list):
                characters.extend(
                    item for item in data if isinstance(item, dict)
                )
        return characters

    def load_one(self, name: str) -> dict[str, Any]:
        """Load a single character card by name.

        Tries ``<slug>.json`` first, then scans all files for a matching
        ``name`` field.  Raises ``FileNotFoundError`` if not found.
        """
        # Fast path: exact filename match
        exact = self.path / f"{_slug(name)}.json"
        if exact.is_file():
            data = load_json(exact)
            if isinstance(data, dict):
                return data

        # Slow path: scan all files
        for fpath in self.list_files():
            data = load_json(fpath)
            if isinstance(data, dict) and data.get("name") == name:
                return data
        raise FileNotFoundError(f"Character not found: {name}")

    def save(self, name: str, data: dict[str, Any]) -> Path:
        """Write (create or update) a character card.

        Returns the path of the written file.
        """
        fpath = self.path / f"{_slug(name)}.json"
        save_json(fpath, data)
        return fpath

    def delete(self, name: str) -> None:
        """Delete a character card file by name.

        Tries ``<slug>.json`` first, then scans files for a matching
        ``name`` field.
        """
        exact = self.path / f"{_slug(name)}.json"
        if exact.is_file():
            delete_file(exact)
            return
        for fpath in self.list_files():
            data = load_json(fpath)
            if isinstance(data, dict) and data.get("name") == name:
                delete_file(fpath)
                return
        raise FileNotFoundError(f"Character not found: {name}")
