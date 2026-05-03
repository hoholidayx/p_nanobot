"""Context routes — build and render RPContext."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from rpg_world.api.deps import get_character_manager, get_lorebook_manager
from rpg_world.rpg_core.character import CharacterManager
from rpg_world.rpg_core.context import RPContext
from rpg_world.rpg_core.lorebook import LorebookManager

router = APIRouter(tags=["context"])


class RenderRequest(BaseModel):
    """Optional request body for context rendering."""
    character_name: str | None = None
    template: str | None = None


@router.post("/context/render")
def render_context(
    body: RenderRequest,
    character_mgr: CharacterManager = Depends(get_character_manager),
    lorebook_mgr: LorebookManager = Depends(get_lorebook_manager),
) -> dict:
    """Build RPContext from current data and render to markdown.

    Only entries with ``enable: true`` are included, unless a specific
    ``character_name`` is requested.
    """
    character: dict = {}
    if body.character_name:
        try:
            character = character_mgr.get_character(body.character_name)
        except FileNotFoundError:
            pass

    if not character:
        # Default to the first enabled character
        enabled = character_mgr.list_enabled_characters()
        character = enabled[0] if enabled else {}

    lore_entries = lorebook_mgr.list_enabled_entries()

    ctx = RPContext(
        character=character,
        lorebook={"entries": lore_entries},
    )
    rendered = ctx.render(template_str=body.template)
    return {
        "rendered": rendered,
        "character_name": character.get("name"),
        "lorebook_entries": len(lore_entries),
    }
