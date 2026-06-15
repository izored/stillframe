"""Anthropic (Claude) adapter — cloud, opt-in only.

Uses the Messages streaming API. Requires ANTHROPIC_API_KEY.
Private / passcoded scenes should never route here (enforced by the reflect
route policy, not this adapter).
"""

from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from ..config import settings
from .base import ProviderAdapter, ProviderInfo

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"


class AnthropicProvider(ProviderAdapter):
    name = "anthropic"
    label = "Claude (cloud)"
    local = False

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key if api_key is not None else settings.anthropic_api_key
        self.model = model or settings.anthropic_model

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": API_VERSION,
            "Content-Type": "application/json",
        }

    async def info(self) -> ProviderInfo:
        if not self.api_key:
            return ProviderInfo(name=self.name, label=self.label, local=self.local,
                                available=False, detail="No ANTHROPIC_API_KEY set.")
        return ProviderInfo(name=self.name, label=self.label, local=self.local,
                            available=True, models=[self.model], default_model=self.model)

    async def stream(
        self, system_prompt: str, user_text: str, model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise RuntimeError("Anthropic requires ANTHROPIC_API_KEY.")
        payload = {
            "model": model or self.model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_text}],
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", API_URL, json=payload, headers=self._headers()) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:"):].strip()
                    if not data:
                        continue
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if event.get("type") == "content_block_delta":
                        chunk = (event.get("delta") or {}).get("text", "")
                        if chunk:
                            yield chunk
                    elif event.get("type") == "message_stop":
                        break
