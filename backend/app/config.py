"""Environment-driven settings for the Stillframe backend."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    stillframe_env: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:5180"

    # Profile: "public" ships empty (defaults, no personal data).
    # "creator" loads personal overrides (db, presence/boundaries, secrets)
    # that live under instance/ and are never committed.
    stillframe_profile: str = "public"

    # Persistence. Public default is an empty gitignored data dir.
    # Creator points DB_PATH at instance/ (also gitignored).
    db_path: str = "./data/stillframe.db"

    # Editable Editor identity. Blank = packaged defaults (presence.md /
    # boundaries.md in the prompts package). Creator sets these to personal,
    # gitignored override files under instance/.
    presence_path: str = ""
    boundaries_path: str = ""

    # Provider selection
    active_provider: str = "ollama"

    # Ollama
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = ""  # blank = auto-detect first available

    # OpenAI-compatible
    openai_base_url: str = "http://host.docker.internal:8080/v1"
    openai_api_key: str = ""
    openai_model: str = ""

    # Anthropic (cloud, opt-in)
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-8"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
