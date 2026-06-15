"""Health + readiness, including Ollama reachability."""

from __future__ import annotations

from fastapi import APIRouter

from .. import __version__
from ..config import settings
from ..providers import get_provider

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok", "app": "stillframe-backend", "version": __version__}


@router.get("/health/provider")
async def provider_health():
    """Reachability of the active provider (default: local Ollama)."""
    try:
        provider = get_provider(settings.active_provider)
        info = await provider.info()
        return {
            "active_provider": settings.active_provider,
            "available": info.available,
            "models": info.models,
            "default_model": info.default_model,
            "detail": info.detail,
        }
    except Exception as e:
        return {"active_provider": settings.active_provider, "available": False, "detail": str(e)}
