"""Configuration service for environment variable management and validation."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Server configuration using Pydantic BaseSettings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # GitLab API Settings
    GITLAB_URL: str = ""
    GITLAB_TOKEN: str = ""
    GITLAB_PROJECT_PATH: str = ""
    GITLAB_BRANCH: str = "main"


# Global settings instance
settings = ServerSettings()
