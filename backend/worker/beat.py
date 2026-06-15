import random
from datetime import datetime
from celery.schedules import crontab
from core.celery_app import celery_app
from core.database_sync import SessionLocal
from models.scan_schedule import ScanSchedule
from models.scan import Scan
from worker.tasks import run_scan

celery_app.conf.beat_schedule = {
    "daily-scheduled-scans": {
        "task": "worker.beat.trigger_scheduled_scans",
        "schedule": crontab(hour=0, minute=0),  # 매일 자정에 실행
    },
}

@celery_app.task(name="worker.beat.trigger_scheduled_scans")
def trigger_scheduled_scans():
    """
    매일 자정에 활성화된 스케줄을 확인하고,
    조건에 부합하는 대상을 1분~4시간 사이의 임의 지연(countdown)을 주어 스캔 실행
    """
    db = SessionLocal()
    try:
        today = datetime.utcnow()
        schedules = db.query(ScanSchedule).filter(
            ScanSchedule.is_enabled == True
        ).all()

        triggered = 0
        for schedule in schedules:
            should_run = False

            if schedule.frequency == "daily":
                should_run = True
            elif schedule.frequency == "weekly":
                # today.weekday()는 0(월) ~ 6(일)
                should_run = (today.weekday() == schedule.day_of_week)
            elif schedule.frequency == "monthly":
                should_run = (today.day == 1)

            if should_run:
                scan = Scan(
                    user_id=schedule.user_id,
                    target_url=f"https://{schedule.domain}",
                    domain=schedule.domain,
                    status="pending",
                )
                db.add(scan)
                db.commit()

                # 1분(60초) ~ 4시간(14400초) 사이의 임의 지연
                jitter_seconds = random.randint(60, 14400)
                run_scan.apply_async(
                    args=[str(scan.id)],
                    countdown=jitter_seconds,  # Thundering Herd 방지
                )
                triggered += 1

        print(f"[Beat] 자동 스캔 {triggered}건 스케줄링 완료 (분산 실행)")
    finally:
        db.close()
