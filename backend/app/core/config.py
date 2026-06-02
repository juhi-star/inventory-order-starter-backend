from __future__ import annotations

from functools import cached_property

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_log_level: str = "INFO"
    app_cors_origins: str = "http://localhost:5173"

    database_url: str
    redis_url: str = "redis://redis:6379/0"

    jwt_secret: str = Field(min_length=32)
    jwt_access_token_ttl_seconds: int = 900
    jwt_refresh_token_ttl_seconds: int = 2592000
    jwt_algorithm: str = "HS256"

    seed_admin_email: str = "admin@example.com"
    seed_admin_password: str = Field(min_length=8)

    @cached_property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.app_cors_origins.split(",") if origin.strip()]

    @cached_property
    def database_url_async(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and "+" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @cached_property
    def database_url_sync(self) -> str:
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and "+" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
