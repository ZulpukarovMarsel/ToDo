from typing import Iterable, List, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from pydantic.networks import EmailStr

from models.users import User, Role
from services.users import UserService
from .base_repository import BaseRepository
from .roles import RolesRepository


class UserRepository(BaseRepository):
    model = User

    async def get_all(self, *options):
        stmt = select(self.model).options(selectinload(User.roles))
        if options:
            stmt = stmt.options(*options)
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_data_by_id(self, id: int, *options):
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(selectinload(User.roles))
        )
        if options:
            stmt = stmt.options(*options)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email_and_password(self, email: str, password: str):
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        user = result.scalar_one_or_none()
        if user is None:
            return None

        verify_password = UserService.verify_password(
            password=password,
            hashed_password=user.password
        )
        if not verify_password:
            return None
        return user

    async def _set_roles_by_ids(self, user: User, ids: List[int]) -> None:
        if ids is None:
            return
        ids = list(dict.fromkeys(ids))
        if ids:
            res = await self.db.execute(select(Role).where(Role.id.in_(ids)))
            roles = list(res.scalars().all())
        else:
            roles = []
        user.roles = roles

    async def update_user(self, user_id: int, data: dict[str, Any]) -> User | None:
        user = await self.get_data_by_id(user_id)
        if not user:
            return None
        try:
            for key in ("email", "first_name", "last_name", "password"):
                if key in data:
                    val = data[key]
                    if key == "password" and val:
                        val = UserService.hash_password(val)
                    setattr(user, key, val)

            await self._set_roles_by_ids(user, data.get("roles"))

            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        return await self.get_data_by_id(user_id)

    async def patch_user(self, user_id: int, data: dict[str, Any]) -> User | None:
        user = await self.get_data_by_id(user_id)
        if not user:
            return None
        try:
            if "password" in data:
                pwd = data.pop("password")
                if pwd:
                    user.password = UserService.hash_password(pwd)

            if "roles" in data:
                await self._set_roles_by_ids(user, data.pop("roles"))

            for key, value in data.items():
                setattr(user, key, value)

            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        return await self.get_data_by_id(user_id)

    async def get_user_by_email(self, email: EmailStr):
        result = await self.db.execute(select(self.model).where(self.model.email == email))
        return result.scalar_one_or_none()
