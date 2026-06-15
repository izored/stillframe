"""Memory layer — structured recall over the user's own frames.

Two jobs:
  1. process_frame() — after a frame is completed, extract durable facts and a
     short summary via the active provider, store them. Recurrence raises a
     fact's confidence over time.
  2. build_memory_context() — for a new reflection, assemble a compact context
     block from recency (recent summaries), relevance (FTS5 matches over past
     frames), and state (high-confidence facts). Injected into the system prompt.

Tiers: working / structured (SQLite, here) / semantic (sqlite-vec, later) /
episodic (the Reel). Semantic recall via sqlite-vec is phased in; for now
relevance uses SQLite FTS5 keyword search.

Privacy: extraction is internal metadata and runs on the active provider.
build_memory_context is only sent to a provider when it is local, so personal
memory is never shipped to a cloud model by default.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .db import Frame, StillframeDB
from .providers.base import ProviderAdapter

# Minimal, plain-language extraction prompts. Output parsed defensively.
_SUMMARY_SYS = (
    "Summarize the following personal reflection in one or two plain sentences. "
    "No markdown, no labels, no diagnosis, no advice. Just what happened and how "
    "they seemed to feel, in their own register. Output only the summary."
)
_FACTS_SYS = (
    "Extract durable, factual notes from this reflection that would help remember "
    "the person across future conversations (e.g. people, ongoing situations, "
    "preferences). Do NOT infer diagnoses, motivations, or anything they did not "
    "say. Output a JSON array of objects with keys \"key\", \"value\", "
    "\"confidence\" (0-1). If nothing durable, output []."
)


def _fts_query(text: str) -> str:
    """Build a safe FTS5 OR-query from free text."""
    terms = re.findall(r"\w+", text.lower())
    # drop very short stopword-ish tokens, cap length
    terms = [t for t in terms if len(t) > 2][:20]
    return " OR ".join(terms)


async def _collect(provider: ProviderAdapter, system: str, user: str) -> str:
    chunks: list[str] = []
    async for c in provider.stream(system, user):
        chunks.append(c)
    return "".join(chunks).strip()


def _parse_facts(raw: str) -> list[dict[str, Any]]:
    raw = raw.strip()
    # tolerate code fences or surrounding prose
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1 or end < start:
        return []
    try:
        data = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return []
    out = []
    for item in data if isinstance(data, list) else []:
        if isinstance(item, dict) and item.get("key") and item.get("value"):
            try:
                conf = float(item.get("confidence", 0.7))
            except (TypeError, ValueError):
                conf = 0.7
            out.append({"key": str(item["key"])[:80], "value": str(item["value"])[:400],
                        "confidence": max(0.0, min(1.0, conf))})
    return out


class MemoryStore:
    def __init__(self, db: StillframeDB):
        self.db = db

    @staticmethod
    def _frame_text(frame: Frame) -> str:
        return "\n".join(
            x for x in (frame.captured, frame.reflection, frame.reframe) if x
        ).strip()

    async def process_frame(self, frame: Frame, provider: ProviderAdapter) -> dict[str, Any]:
        """Extract a summary + facts for a completed frame. Best-effort."""
        text = self._frame_text(frame)
        result = {"summary": False, "facts": 0}
        if not text:
            return result

        try:
            summary = await _collect(provider, _SUMMARY_SYS, text)
            if summary:
                self.db.save_summary(frame.id, summary)
                result["summary"] = True
        except Exception:
            pass

        try:
            facts = _parse_facts(await _collect(provider, _FACTS_SYS, text))
            for f in facts:
                self.db.upsert_fact(f["key"], f["value"], f["confidence"])
            result["facts"] = len(facts)
        except Exception:
            pass

        return result

    def build_memory_context(self, query: str, scene_id: str | None = None,
                             k: int = 4) -> str:
        """Assemble recency + relevance + state into a context block."""
        parts: list[str] = []

        facts = self.db.top_facts(8)
        if facts:
            parts.append("Things I remember:\n" + "\n".join(
                f"- {f['key']}: {f['value']}" for f in facts))

        summaries = self.db.recent_summaries(3)
        if summaries:
            parts.append("Recent reflections:\n" + "\n".join(f"- {s}" for s in summaries))

        matches = self.db.search_frames(_fts_query(query), limit=k, scene_id=scene_id)
        if matches:
            parts.append("Related past frames:\n" + "\n".join(
                f"- {m.captured[:160]}" for m in matches))

        return "\n\n".join(parts)
