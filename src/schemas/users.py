from typing import Optional, List
from pydantic import BaseModel
from pydantic.networks import EmailStr

from .roles import RoleSchema


class UserBaseSchema(BaseModel):
    email: EmailStr


class UserLoginSchema(UserBaseSchema):
    password: str


class UserAddSchema(UserLoginSchema):
    first_name: str
    last_name: str


class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    image: str = None
    first_name: str
    last_name: str
    roles: List[RoleSchema] = []

    class Config:
        from_attributes = True


class UserPatchSchema(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: Optional[List[int]] = []
    password: Optional[str] = None

    class Config:
        from_attributes = True
