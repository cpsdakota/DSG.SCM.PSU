"""Configuration management for SCM Device Register CLI."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="SCM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # SCM Authentication
    client_id: str
    client_secret: str
    tsg_id: str

    # API Configuration
    verify_ssl: bool = True
    auth_url: str = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"

    # Device API endpoints (different from main SCM API)
    device_api_base: str = "https://paas-11.prod.panorama.paloaltonetworks.com"
    admin_api_base: str = "https://admin.prod.panorama.paloaltonetworks.com"
    config_api_base: str = "https://paas-11.prod.panorama.paloaltonetworks.com"


# Global settings instance
settings = Settings()
