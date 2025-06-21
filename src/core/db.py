from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from models.base_models import BaseModel
from core.config import settings


class Database:
    def __init__(self, db_url: str) -> None:
        """
        Инициализация базы данных
        """
        self._engine = create_async_engine(db_url)
        """
        Создаем асинхронный движок базы данных
        """
        self._async_session_maker = async_sessionmaker(
                                        bind=self._engine,
                                        expire_on_commit=False)
        """
        Создаем асинхронный sessionmaker для работы с базой данных
        """

    async def create_database(self) -> None:
        """Создаем таблицы в базе данных"""
        async with self._engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator:
        """Асинхронный контекстный менеджер для сессии"""
        async with self._async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()


db_instance = Database(settings.DATA_BASE_URL_asyncpg)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with db_instance.session() as session:
        yield session
