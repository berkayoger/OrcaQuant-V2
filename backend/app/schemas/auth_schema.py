"""Authentication request/response schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str | None = Field(default=None, min_length=3, max_length=24)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class EmailCodeRequest(BaseModel):
    email: EmailStr


class SendVerificationCodeRequest(BaseModel):
    email: EmailStr
    purpose: str


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)


class PasswordResetRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=12)
    new_password: str = Field(min_length=8)


class AuthUser(BaseModel):
    id: str
    email: EmailStr
    username: str | None = None
    role: str
    plan_code: str | None = None
    is_email_verified: bool | None = None


class AuthResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: AuthUser
