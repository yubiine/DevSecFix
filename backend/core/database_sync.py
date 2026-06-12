from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class SyncSettings(BaseSettings):
    postgres_user: str = "devsecfix"
    postgres_password: str = "devsecfix"
    postgres_db: str = "devsecfix"
    postgres_host: str = "db"
    postgres_port: int = 5432
    sync_database_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def resolved_sync_database_url(self) -> str:
        if self.sync_database_url:
            return self.sync_database_url

        return (
            "postgresql+psycopg2://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


sync_settings = SyncSettings()

sync_engine = create_engine(
    sync_settings.resolved_sync_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)
