from celery import Celery
from core.database import settings

celery_app = Celery(
    "devsecfix",
    broker=settings.resolved_celery_broker_url,
    backend=settings.resolved_celery_result_backend,
)
