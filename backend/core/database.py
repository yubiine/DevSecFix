from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Column, DateTime, Integer, MetaData, Table, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class Settings(BaseSettings):
    postgres_user: str = "devsecfix"
    postgres_password: str = "devsecfix"
    postgres_db: str = "devsecfix"
    postgres_host: str = "db"
    postgres_port: int = 5432
    database_url: str | None = None
    redis_url: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return (
            "postgresql+asyncpg://"
            f"{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()

engine = create_async_engine(settings.resolved_database_url, echo=False)
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()
metadata = MetaData()

health_checks = Table(
    "health_checks",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
