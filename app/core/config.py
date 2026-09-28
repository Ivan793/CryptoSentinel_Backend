from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CryptoSentinel API"
    database_url: str
    upload_dir: str = "uploads"
    max_upload_mb: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()