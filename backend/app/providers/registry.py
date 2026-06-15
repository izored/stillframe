"""Provider registry — resolve a provider by name, list all for the picker."""

from __future__ import annotations

from .base import ProviderAdapter
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider
from .anthropic import AnthropicProvider

_REGISTRY: dict[str, type[ProviderAdapter]] = {
    OllamaProvider.name: OllamaProvider,
    OpenAICompatProvider.name: OpenAICompatProvider,
    AnthropicProvider.name: AnthropicProvider,
}


def get_provider(name: str) -> ProviderAdapter:
    cls = _REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown provider '{name}'. Available: {', '.join(_REGISTRY)}")
    return cls()


def list_providers() -> list[ProviderAdapter]:
    return [cls() for cls in _REGISTRY.values()]
