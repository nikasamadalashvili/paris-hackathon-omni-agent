from __future__ import annotations

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
)

load_dotenv(".env", override=True)


# Centralized LLM model identifiers
OPENAI_GPT5_NANO_2025_08_07: str = "openai/gpt-5-nano-2025-08-07"
OPENAI_GPT5_MINI_2025_08_07: str = "openai/gpt-5-mini-2025-08-07"


class AppSettings(BaseSettings):
    """Application-wide settings and configuration."""

    scrape_do_token: str = Field(description="API key for scrape.do service")

    # General application settings
    app_name: str = Field(default="Omni Agent", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # HTTP client settings
    default_timeout: float = Field(
        default=60.0, description="Default HTTP request timeout in seconds"
    )
    max_retries: int = Field(default=3, description="Maximum number of HTTP retries")

    # Content processing settings
    max_content_length: int = Field(
        default=10000, description="Maximum content length for processing"
    )

    groq_api_key: str = Field(default="", description="Groq API key")

    # Lightpanda remote browser/CDP settings
    lightpanda_ws_base: str = Field(
        default="wss://cloud.lightpanda.io/ws",
        description="Lightpanda WebSocket base URI for CDP",
    )
    lightpanda_token: str = Field(default="", description="Lightpanda access token")


# Create application settings instance
settings = AppSettings()
