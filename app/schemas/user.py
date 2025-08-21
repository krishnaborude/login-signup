from pydantic import BaseModel, field_validator
from uuid import UUID
import re
from email_validator import validate_email, EmailNotValidError

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

def validate_display_name(display_name: str) -> str:
    if re.search(r"\d", display_name):
        raise ValueError("Display name cannot contain numbers")
    if len(display_name) < 2:
        raise ValueError("Display name must be at least 2 characters long")
    if len(display_name) > 50:
        raise ValueError("Display name cannot be longer than 50 characters")
    if not display_name.replace(" ", "").isalpha():
        raise ValueError("Display name can only contain letters and spaces")
    return display_name

class UserBase(BaseModel):
    display_name: str
    email: str
    
    @field_validator("email")
    def validate_email(cls, v):
        try:
            validate_email(v)
            return v.lower()  # normalize email to lowercase
        except EmailNotValidError:
            raise ValueError("Invalid email format")

    @field_validator("display_name")
    def validate_display_name_field(cls, v):
        return validate_display_name(v)

class UserCreate(UserBase):
    password: str
    
    @field_validator("password")
    def validate_password_field(cls, v):
        return validate_password(v)

class User(UserBase):
    id: UUID
    welcome_message: str | None = None

    class Config:
        from_attributes = True
