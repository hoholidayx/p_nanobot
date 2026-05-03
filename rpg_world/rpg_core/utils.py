"""Shared utilities for RPG World data loading.

Handles reading/writing JSON data from a file path or a directory of JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> list[dict[str, Any]] | dict[str, Any]:
    """Read JSON data from *path*.

    - If *path* is a file, reads and returns its content.
    - If *path* is a directory, reads all ``.json`` files (sorted) and
      merges them::
        - Each file can contain a single dict or a list of dicts.
        - Lists are concatenated; dicts are merged (last writer wins).

    Returns the parsed data (a single dict or a list of dicts).
    """
    p = Path(path)
    if p.is_file():
        return _read_json(p)
    if p.is_dir():
        return _load_json_dir(p)
    raise FileNotFoundError(f"Path does not exist: {path}")


def save_json(path: str | Path, data: Any) -> None:
    """Write *data* as JSON to *path* (creates parent dirs if needed)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_file(path: str | Path) -> None:
    """Delete the file at *path* if it exists."""
    Path(path).unlink(missing_ok=True)


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_json_dir(path: Path) -> list[dict[str, Any]] | dict[str, Any]:
    merged_list: list[dict[str, Any]] = []
    merged_dict: dict[str, Any] = {}
    saw_list = False
    saw_dict = False

    for fpath in sorted(path.iterdir()):
        if fpath.suffix.lower() != ".json":
            continue
        data = _read_json(fpath)
        if isinstance(data, list):
            merged_list.extend(data)
            saw_list = True
        elif isinstance(data, dict):
            merged_dict.update(data)
            saw_list = True  # treat dict as a single-item list
            merged_list.append(data)

    if saw_list:
        return merged_list
    return merged_dict
