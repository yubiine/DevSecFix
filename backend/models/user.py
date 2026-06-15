import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    daily_scan_limit = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    verifications = relationship("Verification", back_populates="user")
    scans = relationship("Scan", back_populates="user")
    scan_schedules = relationship(
        "ScanSchedule",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    notification_settings = relationship(
        "NotificationSetting",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    notification_logs = relationship(
        "NotificationLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
