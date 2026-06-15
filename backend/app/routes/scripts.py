"""Scripts — list and fetch guided flows."""

from __future__ import annotations

from fastapi import APIRouter

from ..scripts import list_scripts, get_script

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("")
def scripts():
    return {"data": list_scripts(), "error": None}


@router.get("/{script_id}")
def script(script_id: str):
    data = get_script(script_id)
    if not data:
        return {"data": None, "error": "script_not_found"}
    return {"data": data, "error": None}
