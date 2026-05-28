from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from core.database import engine, settings
from routers import auth, scan


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(settings.redis_url)
    await redis.ping()
    await redis.aclose()

    yield

    await engine.dispose()


app = FastAPI(title="DevSecFix API", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(scan.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
