"""Provider abstraction.

All providers are HTTP-based and async. A provider knows how to:
  1. report whether it is reachable + which models it offers
  2. stream a reflection response given a system prompt + user text

Frontends never talk to providers directly. The reflect route wraps every
provider call in the Safe Set safety layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator


@dataclass
class ProviderInfo:
    name: str            # "ollama" | "openai_compat" | "anthropic"
    label: str           # human label for "Choose your editor"
    local: bool          # True = runs on the user's machine (privacy default)
    available: bool      # reachable / configured right now
    models: list[str] = field(default_factory=list)
    default_model: str = ""
    detail: str = ""     # error or status note


class ProviderAdapter(ABC):
    name: str = "base"
    label: str = "Base"
    local: bool = False

    @abstractmethod
    async def info(self) -> ProviderInfo:
        """Report reachability and available models."""
        ...

    @abstractmethod
    async def stream(
        self,
        system_prompt: str,
        user_text: str,
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield response text chunks as they arrive."""
        ...
