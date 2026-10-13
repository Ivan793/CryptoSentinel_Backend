from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CryptoSentinel API"
    database_url: str
    upload_dir: str = "uploads"
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    test_database_url: str | None = None

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
settings = Settings()