"""Shared Pydantic models for RPG World API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CharacterData(BaseModel):
    """Character card — ``name``, ``enable``, ``content`` are fixed; extra fields allowed."""

    model_config = ConfigDict(extra="allow")

    name: str
    enable: bool = False
    content: str = ""


class LorebookEntry(BaseModel):
    """Lorebook entry — ``name``, ``enable``, ``content`` are fixed; extra fields allowed."""

    model_config = ConfigDict(extra="allow")

    name: str
    enable: bool = False
    content: str = ""
