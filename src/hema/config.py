from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    ROOT: Path = Path(__file__).parent.parent.parent
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
    )


settings = Settings()
