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


class SnippetResponse(BaseModel):
    server_type: str = Field(alias="serverType")
    title: str
    code: str

    model_config = ConfigDict(populate_by_name=True)


class VulnerabilityResponse(BaseModel):
    type: str
    title: str
    detail: str | None = None
    severity: str
    cvss_score: float = Field(alias="cvssScore")
    snippets: list[SnippetResponse] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class ScanDetailResponse(BaseModel):
    task_id: UUID = Field(alias="taskId")
    target: str
    status: str
    security_grade: str | None = Field(default=None, alias="securityGrade")
    total_score: float | None = Field(default=None, alias="totalScore")
    scanned_at: datetime = Field(alias="scannedAt")
    vulnerabilities: list[VulnerabilityResponse] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
