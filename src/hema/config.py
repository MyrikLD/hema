from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    ROOT: Path = Path(__file__).parent.parent.parent


settings = Settings()
