"""LorebookManager — manage lorebook entries with full CRUD."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rpg_world.rpg_core.lorebook.loader import LorebookLoader


class LorebookManager:
    """Manages lorebook entries in memory with CRUD operations.

    Supports both single-file and directory-backed storage.
    """

    def __init__(self, path: str | Path) -> None:
        self.loader = LorebookLoader(path)
        self.data: dict[str, Any] = {}  # will hold {"entries": [...]}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> dict[str, Any]:
        """Load all entries from disk into memory.

        Returns ``self.data`` for convenience.
        """
        entries = self.loader.load()
        self.data = {"entries": entries}
        return self.data

    def reload(self) -> dict[str, Any]:
        """Alias for ``load()`` — re-reads all files from disk."""
        return self.load()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_entries(self) -> list[dict[str, Any]]:
        """Return all lorebook entries."""
        if not self.data:
            self.load()
        return self.data.get("entries", [])

    def list_enabled_entries(self) -> list[dict[str, Any]]:
        """Return only entries where ``enable`` is ``True``."""
        return [e for e in self.list_entries() if e.get("enable")]

    def get_entry(self, name: str) -> dict[str, Any]:
        """Return a single entry by name.

        Raises ``FileNotFoundError`` if not found.
        """
        if not self.data:
            self.load()

        for entry in self.data.get("entries", []):
            if entry.get("name") == name:
                return entry

        # Try fresh disk lookup before failing
        try:
            entry = self.loader.load_one(name)
            self.data.setdefault("entries", []).append(entry)
            return entry
        except FileNotFoundError:
            raise FileNotFoundError(f"Lorebook entry not found: {name}") from None

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def create_entry(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new lorebook entry.

        Requires at least a ``name`` key in *data*.  Persists to disk.
        Returns the stored dict.
        """
        name = data.get("name")
        if not name:
            raise ValueError("Entry must have a 'name' field")

        entries = self.list_entries()
        if any(e.get("name") == name for e in entries):
            raise ValueError(f"Entry already exists: {name}")

        data.setdefault("content", "")
        entries.append(data)

        self._persist(entries)
        return data

    def update_entry(self, name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing lorebook entry.

        If the ``name`` field in *data* differs from *name*, the entry
        is renamed.  Raises ``FileNotFoundError`` if *name* does not
        exist.
        """
        entries = self.list_entries()
        idx = next(
            (i for i, e in enumerate(entries) if e.get("name") == name),
            None,
        )
        if idx is None:
            raise FileNotFoundError(f"Lorebook entry not found: {name}")

        new_name = data.get("name", name)
        if new_name != name:
            merged = dict(entries[idx])
            merged.update(data)
            entries[idx] = merged
        else:
            entries[idx].update(data)

        self._persist(entries)
        return entries[idx]

    def delete_entry(self, name: str) -> None:
        """Delete a lorebook entry by name.

        Raises ``FileNotFoundError`` if *name* does not exist.
        """
        entries = self.list_entries()
        idx = next(
            (i for i, e in enumerate(entries) if e.get("name") == name),
            None,
        )
        if idx is None:
            raise FileNotFoundError(f"Lorebook entry not found: {name}")

        entries.pop(idx)
        self._persist(entries)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _persist(self, entries: list[dict[str, Any]]) -> None:
        """Write the entry list to disk and update in-memory state."""
        self.loader.save_all(entries)
        self.data = {"entries": entries}
