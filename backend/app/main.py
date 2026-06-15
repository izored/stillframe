"""Stillframe backend — FastAPI app.

API-first: this backend is the single source of business, safety, memory, and
(later) evolution logic. The Docker web client and the planned Swift macOS app
are both thin clients over this same contract.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import settings
from .routes import frames, health, providers, reflect, scenes, scripts

app = FastAPI(
    title="Stillframe",
    version=__version__,
    description="Local-first mental wellness workspace. Not therapy, diagnosis, or crisis care.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(providers.router)
app.include_router(scenes.router)
app.include_router(frames.router)
app.include_router(scripts.router)
app.include_router(reflect.router)


@app.get("/")
def root():
    return {
        "app": "Stillframe",
        "tagline": "When life won't pause, your thoughts still can.",
        "disclaimer": "Stillframe supports reflection. It is not therapy, diagnosis, or crisis care.",
        "docs": "/docs",
    }
