"""CharacterManager — manage character cards with full CRUD."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rpg_world.rpg_core.character.loader import CharacterLoader


class CharacterManager:
    """Manages character cards in memory with CRUD operations.

    Data layout — one ``.json`` file per character::

        path/
        ├── alice.json    {"name":"Alice", "content":"…", …}
        └── bob.json      {"name":"Bob",   "content":"…", …}
    """

    def __init__(self, path: str | Path) -> None:
        self.loader = CharacterLoader(path)
        self.data: dict[str, dict[str, Any]] = {}  # name → card

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self) -> dict[str, dict[str, Any]]:
        """Load all character cards from disk into memory.

        Returns ``self.data`` for convenience.
        """
        self.data = {}
        for card in self.loader.load_all():
            name = card.get("name")
            if name:
                self.data[name] = card
        return self.data

    def reload(self) -> dict[str, dict[str, Any]]:
        """Alias for ``load()`` — re-reads all files from disk."""
        return self.load()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_characters(self) -> list[dict[str, Any]]:
        """Return all character cards (shallow copy list)."""
        if not self.data:
            self.load()
        return list(self.data.values())

    def list_enabled_characters(self) -> list[dict[str, Any]]:
        """Return only character cards where ``enable`` is ``True``."""
        return [c for c in self.list_characters() if c.get("enable")]

    def get_character(self, name: str) -> dict[str, Any]:
        """Return a single character card by name.

        Raises ``FileNotFoundError`` if not found.
        """
        if not self.data:
            self.load()
        card = self.data.get(name)
        if card is None:
            # Try a fresh disk lookup before failing
            try:
                card = self.loader.load_one(name)
                self.data[card["name"]] = card
            except FileNotFoundError:
                raise FileNotFoundError(f"Character not found: {name}") from None
        return card

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def create_character(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new character card.

        Requires at least a ``name`` key in *data*.  Persists to disk.
        Returns the stored dict.
        """
        name = data.get("name")
        if not name:
            raise ValueError("Character must have a 'name' field")
        # Ensure data is loaded from disk before checking duplicates
        self.list_characters()
        if name in self.data:
            raise ValueError(f"Character already exists: {name}")

        data.setdefault("content", "")
        self.loader.save(name, data)
        self.data[name] = data
        return data

    def update_character(self, name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing character card.

        Returns the updated dict.  If the ``name`` field in *data*
        differs from *name*, the old file is removed.
        Raises ``FileNotFoundError`` if *name* does not exist.
        """
        # Ensure the target exists
        self.get_character(name)

        new_name = data.get("name", name)
        if new_name != name:
            # Rename — merge old entry into new data, remove old file
            old = dict(self.data.get(name, {}))
            old.update(data)
            old["name"] = new_name
            self.loader.delete(name)
            self.data.pop(name, None)
            self.loader.save(new_name, old)
            self.data[new_name] = old
            return old
        else:
            self.loader.save(name, data)
            self.data[name] = data
        return data

    def delete_character(self, name: str) -> None:
        """Delete a character card.

        Raises ``FileNotFoundError`` if *name* does not exist.
        """
        self.get_character(name)  # ensure exists
        self.loader.delete(name)
        self.data.pop(name, None)
