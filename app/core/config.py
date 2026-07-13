"""Application configuration using pydantic-settings (12-factor)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "federal-workforce-predictor"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Database - SQLite for simplicity, but designed for easy swap
    database_url: str = "sqlite+aiosqlite:///./data/spend.db"
    # Pool settings (even for SQLite, use best practices)
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True

    # Auth - Auth0 primary, Keycloak via same mechanism
    # For demo: we use local RSA keys so everything works offline
    # In prod: set JWKS_URL + issuer + audience
    auth_jwks_url: str | None = None
    auth_issuer: str = "https://example.auth0.com/"  # override via env for real
    auth_audience: str = "https://api.federal-workforce-predictor.example.com"
    # Local test keys (generated at startup for dev/CI - NEVER for prod)
    use_local_test_keys: bool = True
    # For client_id/client_secret flow helper (demo only)
    auth0_client_id: str | None = None
    auth0_client_secret: str | None = None
    auth0_token_url: str | None = None

    # LLM / Agent (LiteLLM compatible model string)
    # Default to local Ollama for template (zero cost, offline, deterministic)
    llm_model: str = "ollama/llama3.2"  # or "gpt-4o-mini", "anthropic/claude-3-5-sonnet-20240620"
    llm_timeout_seconds: int = 30
    llm_max_tokens: int = 800

    # Rate limiting (high traffic protection)
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 10

    # Ethics / feature flags
    require_consent_for_social: bool = True
    enable_synthetic_social: bool = True
    max_recommendation_categories: int = 8

    # GraphQL safety limits (prevent nesting/troublesome queries)
    graphql_max_query_depth: int = 3
    graphql_max_query_cost: int = 50

    # MCP
    mcp_enabled: bool = True

    # Paths
    data_dir: Path = Path("./data")

    @field_validator("data_dir", mode="before")
    @classmethod
    def ensure_data_dir(cls, v: str | Path) -> Path:
        p = Path(v)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def effective_jwks_url(self) -> str | None:
        if self.use_local_test_keys:
            return None  # handled specially in security
        return self.auth_jwks_url


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
