from typing import Optional
from pydantic import BaseModel, EmailStr
from fastapi import UploadFile

class EmailSchema(BaseModel):
    to: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    subject: str
    body: str
    attachment: Optional[UploadFile] = None
