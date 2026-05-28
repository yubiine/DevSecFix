from uuid import UUID

from sqlalchemy import delete

from core.celery_app import celery_app
from core.database_sync import SessionLocal
from core.parser import parse_scan_result
from core.scorer import calculate_security_grade
from core.scanner.orchestrator import run_full_scan
from models.scan import Scan
from models.vulnerability import Vulnerability


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=300,
    task_soft_time_limit=270,
)


@celery_app.task(name="worker.run_scan", bind=True, max_retries=1)
def run_scan(self, scan_id: str):
    db = SessionLocal()
    try:
        scan = db.get(Scan, UUID(scan_id))
        if scan is None:
            return {"status": "not_found", "scan_id": scan_id}

        scan.status = "running"
        db.commit()

        try:
            raw_result = run_full_scan(scan.target_url)
            vulnerabilities = parse_scan_result(raw_result)
            grade, total_score = calculate_security_grade(vulnerabilities)

            db.execute(delete(Vulnerability).where(Vulnerability.scan_id == scan.id))
            for vulnerability in vulnerabilities:
                db.add(
                    Vulnerability(
                        scan_id=scan.id,
                        type=vulnerability["type"],
                        title=vulnerability["title"],
                        detail=vulnerability["detail"],
                        severity=vulnerability["severity"],
                        cvss_score=vulnerability["cvss_score"],
                    )
                )

            scan.result = raw_result
            scan.security_grade = grade
            scan.total_score = total_score
            scan.status = "done"
            db.commit()
            return {"status": "done", "scan_id": scan_id}
        except Exception as exc:
            db.rollback()
            scan = db.get(Scan, UUID(scan_id))
            if scan is not None:
                scan.status = "failed"
                scan.result = {"error": str(exc)}
                db.commit()
            return {"status": "failed", "scan_id": scan_id, "error": str(exc)}
    finally:
        db.close()
