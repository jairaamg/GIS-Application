from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+asyncpg://gis:gis_dev_only@localhost:5432/gis"
    nats_url: str = "nats://localhost:4222"
    valkey_url: str = "redis://localhost:6379/0"
    object_store_endpoint: str = "http://localhost:8333"
    oidc_issuer: str = "http://localhost:8080/realms/gis"
    oidc_client_id: str = "gis-web"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    service_name: str = "api-gateway"


@lru_cache
def get_settings() -> Settings:
    return Settings()
