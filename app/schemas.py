from pydantic import BaseModel, EmailStr, field_validator, constr
from uuid import UUID
import re

def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password

class UserBase(BaseModel):
    username: str
    email: EmailStr  # EmailStr automatically validates email format

class UserCreate(UserBase):
    password: str
    
    @field_validator("password")
    def validate_password_field(cls, v):
        return validate_password(v)

class User(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username_or_email": "your_username_or_email",
                "password": "your_password"
            }
        }
        
    # Rename the field in the API documentation

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)

        # Reorder properties manually
        props = schema.get("properties", {})
        reordered_props = {
            "username_or_email": props.get("username_or_email"),
            "password": props.get("password"),
        }
        schema["properties"] = reordered_props

        # Ensure required order too
        schema["required"] = ["username_or_email", "password"]

        return schema

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
    @field_validator("new_password")
    def validate_password_field(cls, v):
        return validate_password(v)

class PasswordResetResponse(BaseModel):
    message: str
    reset_token: str | None = None