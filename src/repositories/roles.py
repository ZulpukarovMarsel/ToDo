from sqlalchemy import select
from .base_repository import BaseRepository
from models.users import Role


class RolesRepository(BaseRepository):
    model = Role

    async def get_data_by_slug(self, slug: str):
        result = await self.db.execute(select(self.model).where(self.model.slug == slug))
        return result.scalar_one_or_none()
