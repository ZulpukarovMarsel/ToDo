from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import selectinload

from repositories.users import UserRepository
from services.users import UserService
from schemas.users import UserAddSchema, UserResponseSchema, UserPatchSchema

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(lambda: None)]
)


@router.get("/", response_model=list[UserResponseSchema])
async def get_users(request: Request):
    db = request.state.db
    user_repo = UserRepository(db)
    users = await user_repo.get_all(selectinload(user_repo.model.roles))
    return users


@router.get("/{user_id}", response_model=UserResponseSchema)
async def get_user_by_id(user_id: int,
                         request: Request):
    db = request.state.db
    user_repo = UserRepository(db)
    user = await user_repo.get_data_by_id(user_id, selectinload(user_repo.model.roles))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponseSchema)
async def create_user(user: UserAddSchema,
                      request: Request):
    db = request.state.db
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = user.dict()
    existing = await user_repo.get_user_by_email(user_data["email"])
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    new_user = await user_service.create_user(user_data)
    return new_user


@router.patch("/{user_id}", response_model=UserResponseSchema)
async def update_user(user_id: int, user: UserPatchSchema,
                      request: Request):
    db = request.state.db
    user_repo = UserRepository(db)
    user_data = user.dict(exclude_unset=True)
    updated_user = await user_repo.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}", response_model=UserResponseSchema)
async def delete_user(user_id: int,
                      request: Request):
    db = request.state.db
    user_repo = UserRepository(db)
    deleted_user = await user_repo.delete_data(user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user
