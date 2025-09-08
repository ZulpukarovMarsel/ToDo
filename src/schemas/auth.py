from typing import Optional, List
from datetime import datetime
from typing_extensions import Self
from pydantic import BaseModel, model_validator
from pydantic.networks import EmailStr
from fastapi import HTTPException, UploadFile, Form, File
from .roles import RoleSchema


class AuthProfileSchema(BaseModel):
    id: int
    email: EmailStr
    image: Optional[str] = None
    first_name: str
    last_name: str
    roles: Optional[List[RoleSchema]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthProfileUpdateSchema:
    def __init__(
        self,
        first_name: Optional[str] = Form(None),
        last_name: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        image: Optional[UploadFile] = File(None),
        roles: Optional[List[RoleSchema]] = None
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.image = image
        self.roles = roles

    def dict(self, exclude_unset=True):
        return {
            k: v for k, v in self.__dict__.items() if v is not None
        }


class AuthLoginSchema(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class AuthLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    email: EmailStr
    full_name: str

    class Config:
        from_attributes = True


class AuthRegisterSchema(AuthLoginSchema):
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class AuthChangePasswordSchema(BaseModel):
    old_password: str
    password: str

    @model_validator(mode='after')
    def check_password(self) -> Self:
        if self.old_password == self.password:
            raise HTTPException(status_code=400, detail="Старый пароль и новый пароль похожи")
        return self


class AuthTokenSchema(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class AuthTokenDataSchema(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class AuthTokenRefreshSchema(BaseModel):
    refresh_token: str

    class Config:
        from_attributes = True


class AuthTokenRefreshResponseSchema(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class OTPSchema(BaseModel):
    email: EmailStr


class OTPCheckSchema(BaseModel):
    email: EmailStr
    code: int

    class Config:
        from_attributes = True
