from pydantic import BaseModel, Field


class AssetRequest(BaseModel):
    domain: str = Field(..., description="등록할 도메인 주소 (예: example.com)")
