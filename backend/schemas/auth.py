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


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=100)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., alias="refreshToken")

    model_config = ConfigDict(populate_by_name=True)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., alias="refreshToken")

    model_config = ConfigDict(populate_by_name=True)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., alias="currentPassword")
    new_password: str = Field(..., min_length=6, max_length=100, alias="newPassword")

    model_config = ConfigDict(populate_by_name=True)


