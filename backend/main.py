from contextlib import asynccontextmanager

from celery import Celery
from fastapi import FastAPI
from redis.asyncio import Redis

from core.database import engine, metadata, settings


celery_app = Celery(
    "devsecfix",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    redis = Redis.from_url(settings.redis_url)
    await redis.ping()
    await redis.aclose()

    yield

    await engine.dispose()


app = FastAPI(title="DevSecFix API", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
