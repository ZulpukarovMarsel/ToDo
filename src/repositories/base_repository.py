from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Type
from models.base_models import BaseModel


class BaseRepository:
    model: Type[BaseModel] = None

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def get_data_by_id(self, id: int):
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def create_data(self, data: dict):
        data = self.model(**data)
        self.db.add(data)
        try:
            await self.db.commit()
            await self.db.refresh(data)
            return data
        except Exception as e:
            await self.db.rollback()
            return e

    async def update_data(self, data_id: int, data: dict):
        get_data = await self.get_data_by_id(data_id)
        if get_data:
            for key, value in data.items():
                setattr(get_data, key, value)
            try:
                await self.db.commit()
            except Exception as e:
                await self.db.rollback()
                raise e
            await self.db.refresh(get_data)
            return get_data
        return None

    async def delete_data(self, data_id: int):
        data = await self.get_data_by_id(data_id)
        if data:
            await self.db.delete(data)
            await self.db.commit()
            return data
        return None
