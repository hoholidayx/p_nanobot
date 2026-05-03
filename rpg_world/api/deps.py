"""Dependency providers — wire up rpg_core managers for FastAPI routes."""

from __future__ import annotations

from functools import lru_cache

from rpg_world.rpg_core.character import CharacterManager
from rpg_world.rpg_core.lorebook import LorebookManager
from rpg_world.rpg_core.settings import settings


@lru_cache
def get_character_manager() -> CharacterManager:
    return CharacterManager(settings.character_path)


@lru_cache
def get_lorebook_manager() -> LorebookManager:
    return LorebookManager(settings.lorebook_path)
