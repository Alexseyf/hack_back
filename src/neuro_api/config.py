"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables and .env file."""

    # Gemini API settings
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    supabase_service_role_key: str

    # CORS
    cors_origins: list[str] = ["*"]

    # API
    api_prefix: str = "/api"
    debug: bool = False


settings = Settings()  # type: ignore[call-arg]
