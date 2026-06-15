import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class ScanSchedule(Base):
    __tablename__ = "scan_schedules"
    __table_args__ = (
        CheckConstraint(
            "frequency IN ('daily', 'weekly', 'monthly')",
            name="ck_scan_schedules_frequency",
        ),
        CheckConstraint(
            "(frequency = 'daily' AND day_of_week IS NULL) OR "
            "(frequency = 'weekly' AND day_of_week BETWEEN 0 AND 6)",
            name="ck_scan_schedules_frequency_day",
        ),
        UniqueConstraint("user_id", "domain", name="uq_scan_schedules_user_domain"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    domain = Column(String(255), nullable=False, index=True)
    frequency = Column(String(20), nullable=False, default="weekly")
    day_of_week = Column(Integer, nullable=True)
    run_time = Column(Time, nullable=False)
    timezone = Column(String(50), nullable=False, default="Asia/Seoul")
    is_enabled = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user = relationship("User", back_populates="scan_schedules")
