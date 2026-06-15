"""Frames — the core unit. CRUD for the Frame / Sit / Reframe loop."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..db import db

router = APIRouter(prefix="/frames", tags=["frames"])


class FrameCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    captured: str = Field(min_length=1)
    scene_id: str | None = None
    mood_score: int | None = Field(default=None, ge=1, le=10)


class FrameUpdate(BaseModel):
    title: str | None = None
    captured: str | None = None
    reflection: str | None = None
    reframe: str | None = None
    scene_id: str | None = None
    mood_score: int | None = Field(default=None, ge=1, le=10)


@router.get("")
def list_frames(scene_id: str | None = None):
    return {"data": [f.__dict__ for f in db.list_frames(scene_id)], "error": None}


@router.post("")
def create_frame(body: FrameCreate):
    frame = db.create_frame(body.title, body.captured, body.scene_id, body.mood_score)
    return {"data": frame.__dict__, "error": None}


@router.get("/{frame_id}")
def get_frame(frame_id: str):
    frame = db.get_frame(frame_id)
    if not frame:
        return {"data": None, "error": "frame_not_found"}
    return {"data": frame.__dict__, "error": None}


@router.patch("/{frame_id}")
def update_frame(frame_id: str, body: FrameUpdate):
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    frame = db.update_frame(frame_id, **fields)
    if not frame:
        return {"data": None, "error": "frame_not_found"}
    return {"data": frame.__dict__, "error": None}


@router.delete("/{frame_id}")
def delete_frame(frame_id: str):
    ok = db.delete_frame(frame_id)
    return {"data": {"deleted": ok}, "error": None if ok else "frame_not_found"}
