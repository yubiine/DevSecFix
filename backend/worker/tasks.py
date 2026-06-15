import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from uuid import UUID

import requests as req_lib  # 동기 requests 사용 (await 금지)
from sqlalchemy import delete, desc

from core.celery_app import celery_app
from core.database_sync import SessionLocal
from core.parser import parse_scan_result
from core.scanner.orchestrator import run_full_scan
from core.scorer import calculate_security_grade
from models.notification import NotificationLog, NotificationSetting
from models.scan import Scan
from models.vulnerability import Vulnerability

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_time_limit=300,
    task_soft_time_limit=270,
)


def _log_notification(db, scan, channel, event_type, message, status, error=None):
    log = NotificationLog(
        user_id=scan.user_id,
        scan_id=scan.id,
        channel=channel,
        event_type=event_type,
        status=status,
        recipient=scan.user.email if channel == "email" else None,
        message=message,
        error_message=error,
    )
    db.add(log)
    db.commit()


def _send_email_sync(to_email: str, message: str, db, scan, event: str):
    """동기 smtplib 사용 — await 금지"""
    try:
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        if not smtp_user or not smtp_password:
            raise ValueError("SMTP_USER 또는 SMTP_PASSWORD가 설정되지 않았습니다.")

        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = "[DevSecFix] 보안 알림"
        msg["From"] = smtp_user
        msg["To"] = to_email

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        _log_notification(db, scan, "email", event, message, "sent")
    except Exception as e:
        _log_notification(db, scan, "email", event, message, "failed", str(e))


def _send_slack_sync(webhook_url: str, message: str, db, scan, event: str):
    """동기 requests 사용 — await 금지"""
    try:
        res = req_lib.post(webhook_url, json={"text": message}, timeout=5)
        status_str = "sent" if res.status_code == 200 else "failed"
        err = None if res.status_code == 200 else f"HTTP Status {res.status_code}: {res.text}"
        _log_notification(db, scan, "slack", event, message, status_str, err)
    except Exception as e:
        _log_notification(db, scan, "slack", event, message, "failed", str(e))


def _send_kakaowork_sync(webhook_url: str, message: str, db, scan, event: str):
    """동기 requests 사용 — await 금지"""
    try:
        res = req_lib.post(webhook_url, json={"text": message}, timeout=5)
        status_str = "sent" if res.status_code == 200 else "failed"
        err = None if res.status_code == 200 else f"HTTP Status {res.status_code}: {res.text}"
        _log_notification(db, scan, "kakaowork", event, message, status_str, err)
    except Exception as e:
        _log_notification(db, scan, "kakaowork", event, message, "failed", str(e))


def _build_message(event: str, scan) -> str:
    messages = {
        "score_drop": f"[DevSecFix] {scan.domain} 보안 점수가 하락했습니다. 현재 등급: {scan.security_grade}",
        "certificate_expiry": f"[DevSecFix] {scan.domain} SSL 인증서가 30일 이내 만료됩니다.",
        "new_vulnerability": f"[DevSecFix] {scan.domain} 에서 Critical 취약점이 발견되었습니다.",
    }
    return messages.get(event, f"[DevSecFix] {scan.domain} 보안 점검 알림")


def send_notifications_if_needed(scan, db):
    """
    ⚠️ async def 금지 — 일반 동기 함수로 구현
    Celery 태스크(동기)에서 직접 호출 가능
    """
    settings = db.query(NotificationSetting).filter(
        NotificationSetting.user_id == scan.user_id
    ).first()

    if not settings:
        return

    events_to_notify = []

    # 조건 1: 점수 하락
    if settings.notify_score_drop:
        prev_scan = db.query(Scan).filter(
            Scan.user_id == scan.user_id,
            Scan.domain == scan.domain,
            Scan.status == "done",
            Scan.id != scan.id,
        ).order_by(desc(Scan.created_at)).first()

        if prev_scan and prev_scan.total_score is not None and scan.total_score is not None:
            if scan.total_score < prev_scan.total_score:
                events_to_notify.append("score_drop")

    # 조건 2: 인증서 만료 임박 (30일 이내)
    if settings.notify_certificate_expiry:
        ssl_data = (scan.result or {}).get("ssl_scan", {})
        cert_expiry = ssl_data.get("cert_expiry")
        if cert_expiry:
            try:
                # Format: "YYYY-MM-DD" or similar
                expiry_date = datetime.strptime(cert_expiry.split()[0], "%Y-%m-%d")
                if (expiry_date - datetime.utcnow()).days <= 30:
                    events_to_notify.append("certificate_expiry")
            except Exception:
                pass

    # 조건 3: 신규 Critical 취약점
    if settings.notify_new_vulnerability:
        critical_count = db.query(Vulnerability).filter(
            Vulnerability.scan_id == scan.id,
            Vulnerability.severity == "critical",
        ).count()
        if critical_count > 0:
            events_to_notify.append("new_vulnerability")

    for event in events_to_notify:
        message = _build_message(event, scan)

        if settings.email_enabled and settings.email_address:
            _send_email_sync(settings.email_address, message, db, scan, event)

        if settings.slack_enabled and settings.slack_webhook_url:
            _send_slack_sync(settings.slack_webhook_url, message, db, scan, event)

        if settings.kakaowork_enabled and settings.kakaowork_webhook_url:
            _send_kakaowork_sync(settings.kakaowork_webhook_url, message, db, scan, event)


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

            # 발송 조건이 되면 알림 발송 (동기식)
            send_notifications_if_needed(scan, db)

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
