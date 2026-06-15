import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class InvalidatedToken(Base):
    __tablename__ = "invalidated_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String(512), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
