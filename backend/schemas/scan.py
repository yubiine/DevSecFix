from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ScanCreateRequest(BaseModel):
    target_url: str = Field(alias="targetUrl")

    model_config = ConfigDict(populate_by_name=True)


class ScanResponse(BaseModel):
    task_id: UUID = Field(alias="taskId")
    status: str
    result: dict[str, Any] | None = None
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(populate_by_name=True)
