from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class RoleAddSchema(BaseModel):
    name: str


class RoleUpdateSchema(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None


class RoleSchema(RoleAddSchema):
    id: int
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
