from pydantic import BaseModel, ConfigDict, Field


class VerificationRequest(BaseModel):
    domain: str
    method: str = Field(pattern="^(dns|file)$")


class VerificationRequestResponse(BaseModel):
    domain: str
    token: str


class VerificationConfirmRequest(BaseModel):
    domain: str


class VerificationConfirmResponse(BaseModel):
    verified: bool


class VerificationInstruction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    domain: str
    method: str
    token: str
    is_verified: bool
