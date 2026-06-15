from pydantic import BaseModel, Field


class ScheduleCreateRequest(BaseModel):
    domain: str = Field(..., description="스케줄 등록할 도메인 주소 (예: example.com)")
    interval: str = Field(
        ...,
        pattern="^(daily|weekly|monthly)$",
        description="스캔 주기 (daily, weekly, monthly)",
    )


class ScheduleResponse(BaseModel):
    id: str
    domain: str
    interval: str
    isEnabled: bool
    createdAt: str
    nextRunAt: str | None = None
