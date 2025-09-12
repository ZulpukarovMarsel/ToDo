import logging
import httpx

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.encoders import jsonable_encoder
from jose import JWTError
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime

from core.config import settings
from repositories.users import UserRepository
from repositories.otp import OTPRepository
from schemas.auth import (
    AuthLoginSchema, AuthLoginResponseSchema,
    AuthProfileSchema, AuthProfileUpdateSchema,
    AuthRegisterSchema,
    AuthChangePasswordSchema, AuthForgotPasswordSchema, AuthResetPasswordSchema,
    AuthTokenRefreshSchema, AuthTokenRefreshResponseSchema,
    OTPSchema, OTPCheckSchema
)
from services.auth import AuthService, OTPService
from services.users import UserService
from services.base_service import BaseService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(lambda: None)]
)


@router.post("/register", response_model=AuthProfileSchema)
async def register(request: Request, auth_data: AuthRegisterSchema):
    db = request.state.db
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = auth_data.dict()
    existing = await user_repo.get_user_by_email(user_data['email'])
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    new_user = await user_service.create_user(user_data)
    return new_user


@router.post("/otp")
async def send_otp(request: Request, data: OTPSchema):
    db = request.state.db
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(data.email)
    code = await OTPService.generatore_code()
    if not user and code:
        message = f"""
            <!DOCTYPE html>
            <html>
                <body>
                    <p>It's your OTP code:</p>
                    <h2 style="font-size: 24px; color: #333; font-weight: bold;">{code}</h2>
                    <p>Copy and paste this code into the app.
                    The code will expire in 5 minutes.</p>
                </body>
            </html>
        """
        send_message = await BaseService.send_message_to_email(
            emails_to=[data.email], message=message
        )
        if send_message:
            otp_data = {
                'email': data.email,
                'code': code
            }
            otp_repo = OTPRepository(db)
            otp = await otp_repo.create_data(otp_data)
            if otp:
                return {
                    "status": "success",
                    "message": f"OTP success send to email: {otp.email}"
                }
            raise HTTPException(status_code=500, detail="Create otp failed")
        raise HTTPException(status_code=500, detail="Send message failed")
    raise HTTPException(status_code=500, detail="Request failed")


@router.post("/otp/check")
async def checking_otp(request: Request, data: OTPCheckSchema):
    db = request.state.db
    otp_repo = OTPRepository(db)
    user_repo = UserRepository(db)

    otp = await otp_repo.get_otp_by_email_code(data.email, data.code)
    if not otp:
        raise HTTPException(status_code=400, detail="Ваш почта или код не правильный")

    time_difference = datetime.now() - otp.created_at
    if time_difference.total_seconds() > 300:
        await otp_repo.delete_data(otp.id)
        raise HTTPException(status_code=400, detail="Ваш код просрочен, получите новый код")

    existing_user = await user_repo.get_user_by_email(data.email)
    if existing_user:
        await otp_repo.delete_data(otp.id)
        raise HTTPException(status_code=409, detail="Пользователь с этим email уже существует")

    try:
        await otp_repo.delete_data(otp.id)
        return {
            "status": "success",
            "message": "Email successfully verified"
        }

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя")


@router.post("/login", response_model=AuthLoginResponseSchema)
async def login(request: Request, auth_data: AuthLoginSchema):
    db = request.state.db
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email_and_password(auth_data.email, auth_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_payload = {"user_id": user.id, "type": "access"}
    refresh_payload = {"user_id": user.id, "type": "refresh"}

    access_token = AuthService().create_token(access_payload, expires_delta=8640000)
    refresh_token = AuthService().create_token(refresh_payload, expires_delta=8640000)

    if not access_token or not refresh_token:
        raise HTTPException(status_code=500, detail="Token creation failed")
    data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": user.email,
            "full_name": user.full_name()
        }
    return JSONResponse(status_code=201, content=jsonable_encoder(data))


@router.post("/change-password")
async def change_password(request: Request, auth_data: AuthChangePasswordSchema):
    user = request.state.user
    password_data = auth_data.dict()
    verify_password = UserService.verify_password(password_data['old_password'], user.password)
    if verify_password:
        user_data = {
            "password": password_data['password']
        }
        await UserRepository(request.state.db).update_user(user_id=user.id, user_data=user_data)
        return JSONResponse(status_code=200, content={"message": "Пароль изменен успешно!"})
    raise HTTPException(status_code=400, detail="Старый пароль написан не правильно")


@router.post("/forgot-password")
async def forgot_password(request: Request, data: AuthForgotPasswordSchema):
    db = request.state.db
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(data.email)
    code = await OTPService.generatore_code()
    if user and code:
        message = f"""
            <!DOCTYPE html>
            <html>
                <body>
                    <p>It's your OTP  for set your password:</p>
                    <h2 style="font-size: 24px; color: #333; font-weight: bold;">{code}</h2>
                    <p>Copy and paste this code into the app.
                    The code will expire in 5 minutes.</p>
                </body>
            </html>
        """
        send_message = await BaseService.send_message_to_email(
            emails_to=[data.email], message=message
        )
        if send_message:
            otp_data = {
                'email': data.email,
                'code': code
            }
            otp_repo = OTPRepository(db)
            otp = await otp_repo.create_data(otp_data)
            if otp:
                return {
                    "status": "success",
                    "message": f"OTP success send to email: {otp.email}"
                }
            raise HTTPException(status_code=500, detail="Create otp failed")
        raise HTTPException(status_code=500, detail="Send message failed")
    raise HTTPException(status_code=500, detail="Request failed")


@router.post('reset-password')
async def reset_password(request: Request, data: AuthResetPasswordSchema):
    db = request.state.db
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(data.email)
    otp_repo = OTPRepository(db)

    otp = await otp_repo.get_otp_by_email_code(data.email, data.code)
    if not otp:
        raise HTTPException(status_code=400, detail="Ваш почта или код не правильный")

    time_difference = datetime.now() - otp.created_at
    if time_difference.total_seconds() > 300:
        await otp_repo.delete_data(otp.id)
        raise HTTPException(status_code=400, detail="Ваш код просрочен, получите новый код")

    if not user:
        await otp_repo.delete_data(otp.id)
        raise HTTPException(status_code=400, detail="Not user is email")

    try:
        user_data = {'password': data.new_password}
        await user_repo.patch_user(user.id, user_data)
        await otp_repo.delete_data(otp.id)
        return {
            "status": "success",
            "message": "Вы успешно обновили пароль"
        }

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя")


@router.get("/me", response_model=AuthProfileSchema)
async def profile(request: Request):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User is not authanticate")
    data = {
        "id": user.id,
        "image": f'{str(request.base_url).rstrip("/")}{user.image}' if user.image else 'none',
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "roles": user.roles,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    return JSONResponse(status_code=200, content=jsonable_encoder(data))


@router.post("/logout")
async def logout(request: Request, response: Response):
    try:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return JSONResponse(
            status_code=200,
            content={"message": "Вы успешно вышли из системы"}
        )

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при выходе из системы")


@router.patch("/me", response_model=AuthProfileSchema)
async def profile_update(request: Request, auth_data: AuthProfileUpdateSchema = Depends()):
    try:
        db = request.state.db
        user = request.state.user
        if not user:
            raise HTTPException(status_code=401, detail="User is not authenticated")
        update_data = auth_data.dict(exclude_unset=True)
        if "image" in update_data:
            update_data.pop("image")

        if auth_data.image:
            image_info = await BaseService.upload_image(auth_data.image, "avatars")
            update_data["image"] = image_info['image_path']
            {str(request.base_url).rstrip("/")}

        user_repo = UserRepository(db)
        profile_updated = await user_repo.patch_user(user.id, update_data)
        if profile_updated.image:
            profile_updated.image = f'{str(request.base_url).rstrip("/")}{profile_updated.image}'
        return AuthProfileSchema.model_validate(profile_updated)

    except Exception as e:
        logger.exception("Ошибка в обновлении профиля")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/refresh", response_model=AuthTokenRefreshResponseSchema)
async def update_access_token(request: Request, auth_data: AuthTokenRefreshSchema):
    user = request.state.user
    auth_data = auth_data.dict()
    try:
        verify_token = AuthService().verify_token(auth_data['refresh_token'])
        if verify_token:
            access_payload = {"user_id": user.id, "type": "access"}

            access_token = AuthService().create_token(access_payload, expires_delta=8640000)
            data = {
                "access_token": access_token,
                "token_type": "access"
            }
            return JSONResponse(status_code=200, content=jsonable_encoder(data))
    except JWTError as e:
        raise HTTPException(status_code=401, detail=e)
