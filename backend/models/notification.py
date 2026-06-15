import uuid
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base


class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    email_enabled = Column(Boolean, nullable=False, default=True)
    email_address = Column(String(255), nullable=True)
    slack_enabled = Column(Boolean, nullable=False, default=False)
    slack_webhook_url = Column(Text, nullable=True)
    kakaowork_enabled = Column(Boolean, nullable=False, default=False)
    kakaowork_webhook_url = Column(Text, nullable=True)
    notify_new_vulnerability = Column(Boolean, nullable=False, default=True)
    notify_score_drop = Column(Boolean, nullable=False, default=True)
    notify_certificate_expiry = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="notification_settings")
    logs = relationship("NotificationLog", back_populates="setting")


class NotificationLog(Base):
    __tablename__ = "notification_logs"
    __table_args__ = (
        CheckConstraint(
            "channel IN ('email', 'slack', 'kakaowork')",
            name="ck_notification_logs_channel",
        ),
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed')",
            name="ck_notification_logs_status",
        ),
        CheckConstraint(
            "event_type IN "
            "('new_vulnerability', 'score_drop', 'certificate_expiry', 'scan_failed')",
            name="ck_notification_logs_event_type",
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    setting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notification_settings.id", ondelete="SET NULL"),
        nullable=True,
    )
    scan_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scans.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    channel = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    recipient = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    detail = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notification_logs")
    setting = relationship("NotificationSetting", back_populates="logs")
    scan = relationship("Scan", back_populates="notification_logs")
