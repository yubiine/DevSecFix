import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    method = Column(String(20), nullable=False)
    token = Column(String(100), nullable=False)
    is_verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
