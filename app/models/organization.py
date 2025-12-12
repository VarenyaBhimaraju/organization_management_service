from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class OrganizationCreate(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('organization_name')
    @classmethod
    def validate_organization_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                'Organization name must contain only alphanumeric characters and underscores'
            )
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class OrganizationUpdate(BaseModel):
    organization_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @field_validator('organization_name')
    @classmethod
    def validate_organization_name(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                'Organization name must contain only alphanumeric characters and underscores'
            )
        return v.lower()


class OrganizationResponse(BaseModel):
    id: str = Field(..., alias="_id")
    organization_name: str
    collection_name: str
    admin_email: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OrganizationInDB(BaseModel):
    organization_name: str
    collection_name: str
    admin_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
