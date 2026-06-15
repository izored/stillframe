"""Load guided Scripts from JSON data files.

A Script is a sequence of gentle steps. Steps map onto the Frame / Sit /
Reframe loop. Content stays in editable JSON so non-developers can revise it.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


@lru_cache(maxsize=1)
def _load_all() -> dict[str, dict]:
    scripts: dict[str, dict] = {}
    for path in sorted(DATA_DIR.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if "id" in data:
            scripts[data["id"]] = data
    return scripts


def list_scripts() -> list[dict]:
    return [
        {"id": s["id"], "name": s["name"], "summary": s.get("summary", ""),
         "steps": len(s.get("steps", []))}
        for s in _load_all().values()
    ]


def get_script(script_id: str) -> dict | None:
    return _load_all().get(script_id)
