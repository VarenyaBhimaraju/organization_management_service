from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    organization_id: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AdminInDB(BaseModel):
    email: str
    hashed_password: str
    organization_id: str
    created_at: datetime
    is_active: bool = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    admin_id: str
    email: str
    organization_id: str
    exp: Optional[datetime] = None
