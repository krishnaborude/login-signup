from pydantic import BaseModel, field_validator
from email_validator import validate_email, EmailNotValidError

class Token(BaseModel):
    welcome_message: str
    message: str
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, v):
        # First check if email contains any uppercase letters
        if any(c.isupper() for c in v):
            raise ValueError("Email must be in lowercase letters only")
            
        try:
            validate_email(v)
            return v  # No need to call lower() since we already ensure it's lowercase
        except EmailNotValidError:
            raise ValueError("Invalid email format")

    @field_validator("password")
    def validate_password_field(cls, v):
        from app.schemas.user import validate_password
        return validate_password(v)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "your.email@example.com",
                "password": "your_password"
            }
        }

class ForgotPasswordRequest(BaseModel):
    email: str

    @field_validator("email")
    def validate_email(cls, v):
        # First check if email contains any uppercase letters
        if any(c.isupper() for c in v):
            raise ValueError("Email must be in lowercase letters only")
            
        try:
            validate_email(v)
            return v  # No need to call lower() since we already ensure it's lowercase
        except EmailNotValidError:
            raise ValueError("Invalid email format")

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

class PasswordResetSuccessResponse(BaseModel):
    message: str
