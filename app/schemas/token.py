from pydantic import BaseModel, field_validator
from email_validator import validate_email, EmailNotValidError

class Token(BaseModel):
    message: str
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

    @field_validator("password")
    def validate_password_field(cls, v):
        from app.schemas.user import validate_password
        return validate_password(v)

    class Config:
        json_schema_extra = {
            "example": {
                "username_or_email": "your_username_or_email",
                "password": "your_password"
            }
        }

class ForgotPasswordRequest(BaseModel):
    username_or_email: str

    @field_validator("username_or_email")
    def validate_username_or_email(cls, v):
        if "@" in v:  # If it looks like an email
            try:
                validate_email(v)
            except EmailNotValidError:
                raise ValueError("Invalid email format")
        return v

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, v):
        from app.schemas.user import validate_password
        return validate_password(v)

class PasswordResetResponse(BaseModel):
    message: str
    reset_token: str
