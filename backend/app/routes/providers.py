"""Provider listing — powers the "Choose your editor" picker."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter

from ..providers import list_providers

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("")
async def providers():
    adapters = list_providers()
    infos = await asyncio.gather(*(a.info() for a in adapters))
    return {
        "data": [
            {
                "name": i.name, "label": i.label, "local": i.local,
                "available": i.available, "models": i.models,
                "default_model": i.default_model, "detail": i.detail,
            }
            for i in infos
        ],
        "error": None,
    }
