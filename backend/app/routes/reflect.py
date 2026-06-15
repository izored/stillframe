"""Reflect — the safety-wrapped streaming AI endpoint.

Every call flows through the Safe Set:
  1. supervisor.begin_turn() classifies the user input. Crisis or policy hit
     returns a safe override and the provider is never called.
  2. otherwise the provider streams, and each chunk passes through the stream
     safety buffer, which can block unsafe output before it reaches the user.

Streaming uses NDJSON (one JSON object per line) so both the web client and a
future SwiftUI client can consume it the same way.
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..config import settings
from ..db import db
from ..prompts import build_system_prompt
from ..providers import get_provider
from ..safety import WellnessSafetySupervisor

router = APIRouter(prefix="/reflect", tags=["reflect"])


class ReflectRequest(BaseModel):
    text: str = Field(min_length=1)
    scene_id: str | None = None
    provider: str | None = None   # override active provider
    model: str | None = None


def _event(kind: str, **data) -> str:
    return json.dumps({"type": kind, **data}) + "\n"


async def _run(req: ReflectRequest) -> AsyncGenerator[str, None]:
    supervisor = WellnessSafetySupervisor()

    # 1. Inbound safety gate.
    decision = supervisor.begin_turn(req.text)
    if not decision.allow_provider:
        yield _event("safety", reason_codes=list(decision.reason_codes),
                     crisis=decision.crisis_detected)
        yield _event("delta", text=decision.override_response or "")
        yield _event("done", blocked=True)
        return

    # 2. Resolve provider, honoring scene privacy (local-only blocks cloud).
    provider_name = req.provider or settings.active_provider
    scene = db.get_scene(req.scene_id) if req.scene_id else None
    provider = get_provider(provider_name)
    if scene and scene.local_only and not provider.local:
        yield _event("error", detail="This scene is local-only. Choose a local provider.")
        yield _event("done", blocked=True)
        return

    system = build_system_prompt(
        safety_guidance=supervisor.prompt_guidance(),
        scene=scene.name if scene else "",
    )

    # 3. Stream through the safety buffer.
    buffer = supervisor.new_stream_buffer()
    try:
        async for chunk in provider.stream(system, req.text, req.model):
            result = buffer.push(chunk)
            if result.blocked:
                yield _event("safety", reason_codes=list(result.reason_codes))
                if result.safe_fallback:
                    yield _event("delta", text=result.safe_fallback)
                yield _event("done", blocked=True)
                return
            if result.released_text:
                yield _event("delta", text=result.released_text)

        tail = buffer.finish()
        if tail.blocked:
            yield _event("safety", reason_codes=list(tail.reason_codes))
            if tail.safe_fallback:
                yield _event("delta", text=tail.safe_fallback)
            yield _event("done", blocked=True)
            return
        if tail.released_text:
            yield _event("delta", text=tail.released_text)

        yield _event("done", blocked=False)
    except Exception as e:
        yield _event("error", detail=str(e))
        yield _event("done", blocked=True)


@router.post("")
async def reflect(req: ReflectRequest):
    return StreamingResponse(_run(req), media_type="application/x-ndjson")
