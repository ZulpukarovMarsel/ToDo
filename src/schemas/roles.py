from typing import Optional
from pydantic import BaseModel
from pydantic.networks import EmailStr
from datetime import datetime


class RoleAddSchema(BaseModel):
    name: str


class RoleSchema(RoleAddSchema):
    id: int
    slug: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
