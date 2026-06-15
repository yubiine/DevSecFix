from pydantic import BaseModel, ConfigDict, Field


class NotificationSettingsUpdateRequest(BaseModel):
    emailEnabled: bool = Field(..., alias="emailEnabled")
    emailAddress: str | None = Field(None, alias="emailAddress")
    slackEnabled: bool = Field(..., alias="slackEnabled")
    slackWebhookUrl: str | None = Field(None, alias="slackWebhookUrl")
    kakaoworkEnabled: bool = Field(..., alias="kakaoworkEnabled")
    kakaoworkWebhookUrl: str | None = Field(None, alias="kakaoworkWebhookUrl")
    notifyNewVulnerability: bool = Field(..., alias="notifyNewVulnerability")
    notifyScoreDrop: bool = Field(..., alias="notifyScoreDrop")
    notifyCertificateExpiry: bool = Field(..., alias="notifyCertificateExpiry")

    model_config = ConfigDict(populate_by_name=True)


class NotificationSettingsResponse(BaseModel):
    emailEnabled: bool
    emailAddress: str | None = None
    slackEnabled: bool
    slackWebhookUrl: str | None = None
    kakaoworkEnabled: bool
    kakaoworkWebhookUrl: str | None = None
    notifyNewVulnerability: bool
    notifyScoreDrop: bool
    notifyCertificateExpiry: bool


class NotificationLogResponse(BaseModel):
    id: str
    channel: str
    eventType: str = Field(..., alias="eventType")
    status: str
    recipient: str | None = None
    message: str
    createdAt: str = Field(..., alias="createdAt")
    sentAt: str | None = Field(None, alias="sentAt")

    model_config = ConfigDict(populate_by_name=True)
