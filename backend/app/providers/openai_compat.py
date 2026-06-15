"""OpenAI-compatible adapter — llama.cpp server, LM Studio, or OpenAI itself.

Uses the /chat/completions streaming (SSE) contract. API key optional
(local OpenAI-compatible servers usually need none).
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from ..config import settings
from .base import ProviderAdapter, ProviderInfo


class OpenAICompatProvider(ProviderAdapter):
    name = "openai_compat"
    label = "OpenAI-compatible"
    local = False  # depends on endpoint; treated as non-local for the privacy default

    def __init__(self, base_url: str | None = None, api_key: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.api_key = api_key if api_key is not None else settings.openai_api_key
        self.model = model or settings.openai_model

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def info(self) -> ProviderInfo:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
                models = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
            default = self.model or (models[0] if models else "")
            return ProviderInfo(
                name=self.name, label=self.label, local=self.local,
                available=bool(models) or bool(self.model), models=models, default_model=default,
            )
        except Exception as e:
            return ProviderInfo(
                name=self.name, label=self.label, local=self.local,
                available=False, detail=f"Unreachable at {self.base_url}: {e}",
            )

    async def stream(
        self, system_prompt: str, user_text: str, model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        use_model = model or self.model
        if not use_model:
            raise RuntimeError("No OpenAI-compatible model configured (OPENAI_MODEL).")
        payload = {
            "model": use_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions",
                                     json=payload, headers=self._headers()) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    delta = (event.get("choices") or [{}])[0].get("delta", {})
                    chunk = delta.get("content", "")
                    if chunk:
                        yield chunk
