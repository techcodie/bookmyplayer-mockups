from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models import Stage

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str | None = None

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str | None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
