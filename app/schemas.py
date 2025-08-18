from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

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
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username or email": "your_username_or_email",
                "password": "your_password"
            }
        }
        
    # Rename the field in the API documentation
    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        # Update the properties to show "username or email" instead of just "username"
        schema["properties"]["username"]["title"] = "username or email"
        schema["properties"]["username"]["description"] = "Enter either your username or email address"
        return schema
