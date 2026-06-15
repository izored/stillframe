"""Scenes — context buckets that can evolve."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..db import db

router = APIRouter(prefix="/scenes", tags=["scenes"])


class SceneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    mood: str = "neutral"
    private: bool = False
    local_only: bool = False


@router.get("")
def list_scenes():
    return {"data": [s.__dict__ for s in db.list_scenes()], "error": None}


@router.post("")
def create_scene(body: SceneCreate):
    scene = db.create_scene(body.name, body.mood, body.private, body.local_only)
    return {"data": scene.__dict__, "error": None}


@router.get("/{scene_id}")
def get_scene(scene_id: str):
    scene = db.get_scene(scene_id)
    if not scene:
        return {"data": None, "error": "scene_not_found"}
    return {"data": scene.__dict__, "error": None}
