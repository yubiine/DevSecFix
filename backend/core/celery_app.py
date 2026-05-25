from celery import Celery
from core.database import settings

celery_app = Celery(
    "devsecfix",
    broker=settings.redis_url,
    backend=settings.redis_url,
)