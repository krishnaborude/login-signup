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