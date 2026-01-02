"""Configuration settings for miu-studio."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    model_config = SettingsConfigDict(env_prefix="MIU_")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["*"]

    # Agent
    default_model: str = "claude-sonnet-4-20250514"
    default_provider: str = "anthropic"
    max_tokens: int = 4096
    max_iterations: int = 10

    # Sessions
    session_dir: str = ".miu/sessions"
    session_timeout: int = 3600  # 1 hour

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


settings = Settings()
