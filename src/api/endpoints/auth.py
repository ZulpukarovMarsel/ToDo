from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import JWTError

from repositories.users import UserRepository
from schemas.auth import (
    AuthLoginSchema, AuthLoginResponseSchema,
    AuthProfileSchema, AuthProfileUpdateSchema,
    AuthRegisterSchema,
    AuthChangePasswordSchema,
    AuthTokenRefreshSchema, AuthTokenRefreshResponseSchema
)
from services.auth import AuthService
from services.users import UserService
from services.base_service import BaseService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(lambda: None)]
)


@router.post("/register", response_model=AuthProfileSchema)
async def register(auth_data: AuthRegisterSchema,
                   request: Request):
    """
    Регистрация нового пользователя.
    """
    db = request.state.db
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = auth_data.dict()
    existing = await user_repo.get_user_by_email(user_data['email'])
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    new_user = await user_service.create_user(user_data)
    return new_user


@router.post("/login", response_model=AuthLoginResponseSchema)
async def login(auth_data: AuthLoginSchema,
                request: Request):
    """
    Вход в систему пользователя.
    """
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
async def change_password(auth_data: AuthChangePasswordSchema, request: Request):
    """
    Изменения пароля пользователя
    """
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


@router.get("/me", response_model=AuthProfileSchema)
async def profile(request: Request):
    """
    Профил
    """
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="User is not authanticate")
    data = {
        "id": user.id,
        "image": f'{str(request.base_url).rstrip("/")}{user.image}' if user.image else 'No photo',
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "roles": user.roles,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    return JSONResponse(status_code=200, content=jsonable_encoder(data))


@router.patch("/me", response_model=AuthProfileSchema)
async def profile_update(auth_data: AuthProfileUpdateSchema = Depends(), request: Request = None):
    """
    Обновления профиля
    """
    logger.info("Запустился API")
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
            update_data["image"] = f'{image_info['image_path']}'
            {str(request.base_url).rstrip("/")}

        user_repo = UserRepository(db)
        profile_updated = await user_repo.update_user(user.id, update_data)
        profile_updated.image = f'{str(request.base_url).rstrip("/")}{profile_updated.image}'
        return AuthProfileSchema.model_validate(profile_updated)

    except Exception as e:
        logger.exception("Ошибка в обновлении профиля")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/uploadfile")
async def create_upload_file(file: UploadFile, request: Request):
    file = await BaseService.upload_image(file, "avatar")
    full_url = f'{str(request.base_url).rstrip("/")}{file['image_path']}'
    return {"filename": full_url}


@router.post("/token/refresh", response_model=AuthTokenRefreshResponseSchema)
async def update_access_token(auth_data: AuthTokenRefreshSchema, request: Request):
    """
    Обновления access токена
    """
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
