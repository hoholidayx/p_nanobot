"""Lorebook routes — full CRUD, delegates to LorebookManager."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from rpg_world.api.deps import get_lorebook_manager
from rpg_world.models import LorebookEntry
from rpg_world.rpg_core.lorebook import LorebookManager

router = APIRouter(tags=["lorebook"])


@router.get("/lorebook/entries")
def list_entries(
    manager: LorebookManager = Depends(get_lorebook_manager),
) -> dict:
    """Return all lorebook entries."""
    return {"entries": manager.list_entries()}


@router.get("/lorebook/entries/{name}")
def get_entry(
    name: str,
    manager: LorebookManager = Depends(get_lorebook_manager),
) -> dict:
    """Return a single lorebook entry by name."""
    try:
        return manager.get_entry(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Entry not found: {name}")


@router.post("/lorebook/entries")
def create_entry(
    body: LorebookEntry,
    manager: LorebookManager = Depends(get_lorebook_manager),
) -> dict:
    """Create a new lorebook entry."""
    try:
        data = manager.create_entry(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return {"status": "created", "data": data}


@router.put("/lorebook/entries/{name}")
def update_entry(
    name: str,
    body: LorebookEntry,
    manager: LorebookManager = Depends(get_lorebook_manager),
) -> dict:
    """Update an existing lorebook entry."""
    try:
        data = manager.update_entry(name, body.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "updated", "data": data}


@router.delete("/lorebook/entries/{name}")
def delete_entry(
    name: str,
    manager: LorebookManager = Depends(get_lorebook_manager),
) -> dict:
    """Delete a lorebook entry."""
    try:
        manager.delete_entry(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"status": "deleted", "name": name}
