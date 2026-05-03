"""RPContext — structured data container for RPG World.

All data is stored as plain dicts and rendered to markdown via Jinja2
at the final step, keeping the data model agnostic to presentation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Template

_DEFAULT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "jinja" / "default_context.jinja"


class RPContext:
    """Root data structure for the RPG World system.

    Attributes:
        lorebook:  World book entries (dict). Managed by LorebookManager.
        character: Character card (dict). Managed by CharacterManager.
    """

    def __init__(
        self,
        lorebook: dict[str, Any] | None = None,
        character: dict[str, Any] | None = None,
    ) -> None:
        self.lorebook: dict[str, Any] = lorebook or {}
        self.character: dict[str, Any] = character or {}

    # ------------------------------------------------------------------
    # Dict-like access for convenient read / merge
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Export all data as a single dict (for Jinja2 rendering)."""
        return {
            "lorebook": self.lorebook,
            "character": self.character,
        }

    def update_lorebook(self, data: dict[str, Any]) -> None:
        self.lorebook.update(data)

    def update_character(self, data: dict[str, Any]) -> None:
        self.character.update(data)

    # ------------------------------------------------------------------
    # Jinja2 rendering
    # ------------------------------------------------------------------

    def render(self, template_str: str | None = None) -> str:
        """Render context to a markdown string via Jinja2.

        Args:
            template_str: Jinja2 template string.  When ``None``, uses the
                          default template from ``jinja/default_context.jinja``.

        Returns:
            Rendered markdown string.
        """
        if template_str is None:
            template_str = _DEFAULT_TEMPLATE_PATH.read_text(encoding="utf-8")
        tpl = Template(template_str)
        return tpl.render(**self.to_dict())
