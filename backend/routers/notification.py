from datetime import datetime
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from core.deps import get_current_user, get_db
from models.user import User
from models.notification import NotificationSetting, NotificationLog
from schemas.notification import (
    NotificationSettingsUpdateRequest,
    NotificationSettingsResponse,
    NotificationLogResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    body: NotificationSettingsUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationSetting).where(NotificationSetting.user_id == current_user.id)
    )
    setting = result.scalar_one_or_none()

    if setting is None:
        setting = NotificationSetting(
            user_id=current_user.id,
            email_enabled=body.emailEnabled,
            email_address=body.emailAddress,
            slack_enabled=body.slackEnabled,
            slack_webhook_url=body.slackWebhookUrl,
            kakaowork_enabled=body.kakaoworkEnabled,
            kakaowork_webhook_url=body.kakaoworkWebhookUrl,
            notify_new_vulnerability=body.notifyNewVulnerability,
            notify_score_drop=body.notifyScoreDrop,
            notify_certificate_expiry=body.notifyCertificateExpiry,
        )
        db.add(setting)
    else:
        setting.email_enabled = body.emailEnabled
        setting.email_address = body.emailAddress
        setting.slack_enabled = body.slackEnabled
        setting.slack_webhook_url = body.slackWebhookUrl
        setting.kakaowork_enabled = body.kakaoworkEnabled
        setting.kakaowork_webhook_url = body.kakaoworkWebhookUrl
        setting.notify_new_vulnerability = body.notifyNewVulnerability
        setting.notify_score_drop = body.notifyScoreDrop
        setting.notify_certificate_expiry = body.notifyCertificateExpiry
        setting.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(setting)

    return NotificationSettingsResponse(
        emailEnabled=setting.email_enabled,
        emailAddress=setting.email_address,
        slackEnabled=setting.slack_enabled,
        slackWebhookUrl=setting.slack_webhook_url,
        kakaoworkEnabled=setting.kakaowork_enabled,
        kakaoworkWebhookUrl=setting.kakaowork_webhook_url,
        notifyNewVulnerability=setting.notify_new_vulnerability,
        notifyScoreDrop=setting.notify_score_drop,
        notifyCertificateExpiry=setting.notify_certificate_expiry,
    )


@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationSetting).where(NotificationSetting.user_id == current_user.id)
    )
    setting = result.scalar_one_or_none()

    if setting is None:
        # Return default settings if not exists yet
        return NotificationSettingsResponse(
            emailEnabled=True,
            emailAddress=current_user.email,
            slackEnabled=False,
            slackWebhookUrl=None,
            kakaoworkEnabled=False,
            kakaoworkWebhookUrl=None,
            notifyNewVulnerability=True,
            notifyScoreDrop=True,
            notifyCertificateExpiry=True,
        )

    return NotificationSettingsResponse(
        emailEnabled=setting.email_enabled,
        emailAddress=setting.email_address,
        slackEnabled=setting.slack_enabled,
        slackWebhookUrl=setting.slack_webhook_url,
        kakaoworkEnabled=setting.kakaowork_enabled,
        kakaoworkWebhookUrl=setting.kakaowork_webhook_url,
        notifyNewVulnerability=setting.notify_new_vulnerability,
        notifyScoreDrop=setting.notify_score_drop,
        notifyCertificateExpiry=setting.notify_certificate_expiry,
    )


@router.get("/logs", response_model=list[NotificationLogResponse])
async def list_notification_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationLog)
        .where(NotificationLog.user_id == current_user.id)
        .order_by(desc(NotificationLog.created_at))
    )
    logs = result.scalars().all()
    return [
        NotificationLogResponse(
            id=str(log.id),
            channel=log.channel,
            eventType=log.event_type,
            status=log.status,
            recipient=log.recipient,
            message=log.message,
            createdAt=log.created_at.isoformat(),
            sentAt=log.sent_at.isoformat() if log.sent_at else None,
        )
        for log in logs
    ]
