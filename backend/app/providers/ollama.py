"""Ollama adapter — first-class local provider (privacy default).

Talks to the Ollama HTTP API (/api/tags, /api/chat). No API key.
Model auto-detection: if no model is configured, the first available is used.
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from ..config import settings
from .base import ProviderAdapter, ProviderInfo


class OllamaProvider(ProviderAdapter):
    name = "ollama"
    label = "Local (Ollama)"
    local = True

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def _tags(self) -> list[str]:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]

    async def info(self) -> ProviderInfo:
        try:
            models = await self._tags()
            default = self.model or (models[0] if models else "")
            return ProviderInfo(
                name=self.name, label=self.label, local=self.local,
                available=bool(models), models=models, default_model=default,
                detail="" if models else "No models pulled. Try: ollama pull llama3.1",
            )
        except Exception as e:
            return ProviderInfo(
                name=self.name, label=self.label, local=self.local,
                available=False, detail=f"Unreachable at {self.base_url}: {e}",
            )

    async def _resolve_model(self, model: str | None) -> str:
        if model:
            return model
        if self.model:
            return self.model
        tags = await self._tags()
        if not tags:
            raise RuntimeError("No Ollama models available. Pull one first (e.g. ollama pull llama3.1).")
        return tags[0]

    async def stream(
        self, system_prompt: str, user_text: str, model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        use_model = await self._resolve_model(model)
        payload = {
            "model": use_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    chunk = (event.get("message") or {}).get("content", "")
                    if chunk:
                        yield chunk
                    if event.get("done"):
                        break
