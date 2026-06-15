"""Provider adapters — HTTP-based, provider-agnostic ("Choose your editor")."""

from .base import ProviderAdapter, ProviderInfo
from .registry import get_provider, list_providers

__all__ = ["ProviderAdapter", "ProviderInfo", "get_provider", "list_providers"]
