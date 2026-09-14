from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Gateway Configuration
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8000
    gateway_prefix: str = "/api/v1"

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Backend Services
    backend_services: str = "http://localhost:8001,http://localhost:8002"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env.local",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def backend_services_list(self) -> list[str]:
        return [service.strip() for service in self.backend_services.split(",")]


settings = Settings()
