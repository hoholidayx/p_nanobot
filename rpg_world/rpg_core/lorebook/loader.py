"""LorebookLoader — load/save lorebook entries from/to JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rpg_world.rpg_core.utils import delete_file, load_json, save_json


def _slug(name: str) -> str:
    return name.lower().replace(" ", "_")


class LorebookLoader:
    """File I/O for lorebook entries.

    Supports two storage layouts:

    **Single file** (default)::

        path/entries.json  →  [{"name":"…","content":"…", …}, …]

    **Directory of entry files**::

        path/
        ├── world_history.json  {"name":"World History","content":"…", …}
        └── magic_system.json   {"name":"Magic System",  "content":"…", …}
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _is_single_file_mode(self) -> bool:
        """Return ``True`` if the path points to a JSON file (single-file mode)."""
        return self.path.is_file() or self.path.suffix.lower() == ".json"

    def _entries_path(self) -> Path:
        """Return the path to the single ``entries.json`` file."""
        return self.path if self._is_single_file_mode() else self.path / "entries.json"

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load(self) -> list[dict[str, Any]]:
        """Load all lorebook entries.

        Returns a list of entry dicts.
        """
        if self._is_single_file_mode():
            p = self._entries_path()
            if not p.is_file():
                return []
            data = load_json(p)
        else:
            if not self.path.is_dir():
                return []
            data = load_json(self.path)

        if isinstance(data, dict):
            return [data]
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        return []

    def load_one(self, name: str) -> dict[str, Any]:
        """Load a single entry by name.

        In directory mode, tries ``<slug>.json`` first, then scans.
        In single-file mode, scans the list.
        """
        if not self._is_single_file_mode():
            exact = self.path / f"{_slug(name)}.json"
            if exact.is_file():
                data = load_json(exact)
                if isinstance(data, dict):
                    return data

        for entry in self.load():
            if entry.get("name") == name:
                return entry
        raise FileNotFoundError(f"Lorebook entry not found: {name}")

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, name: str, data: dict[str, Any]) -> Path:
        """Write (create or update) a single entry.

        In single-file mode, *data* is appended to the list after a
        full ``load()`` + merge cycle (caller must manage the list).
        In directory mode, writes ``<slug>.json``.

        Returns the path that was written to.
        """
        if self._is_single_file_mode():
            return self._entries_path()  # caller must save_all()

        fpath = self.path / f"{_slug(name)}.json"
        save_json(fpath, data)
        return fpath

    def save_all(self, entries: list[dict[str, Any]]) -> Path:
        """Overwrite the entire entry list in single-file mode.

        In directory mode, writes each entry to its own file (removes
        stale files).
        """
        if self._is_single_file_mode():
            p = self._entries_path()
            save_json(p, entries)
            return p

        # Directory mode — write each entry, remove orphans
        self.path.mkdir(parents=True, exist_ok=True)
        seen: set[str] = set()
        for entry in entries:
            ename = entry.get("name", "untitled")
            fpath = self.path / f"{_slug(ename)}.json"
            save_json(fpath, entry)
            seen.add(fpath.name)

        for fpath in self.path.glob("*.json"):
            if fpath.name not in seen:
                delete_file(fpath)

        return self.path

    def delete(self, name: str) -> None:
        """Delete a single entry by name."""
        if not self._is_single_file_mode():
            exact = self.path / f"{_slug(name)}.json"
            if exact.is_file():
                delete_file(exact)
                return

        # Fallback: scan for the name in single-file mode
        # (actual deletion happens at the Manager level)
        raise FileNotFoundError(
            "Use LorebookManager.delete_entry() for single-file mode"
        )
