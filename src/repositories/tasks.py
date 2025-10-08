from sqlalchemy import select

from .base_repository import BaseRepository
from models.tasks import Task, TaskStatus, Priority


class TaskStatusRepository(BaseRepository):
    model = TaskStatus

    async def get_status_by_slug(self, slug: str):
        result = await self.db.execute(
            select(self.model)
            .where(self.model.slug == slug)
        )
        return result.scalar_one_or_none()


class PriorityRepository(BaseRepository):
    model = Priority

    async def get_priority_by_slug(self, slug: str):
        result = await self.db.execute(
            select(self.model)
            .where(self.model.slug == slug)
        )
        return result.scalar_one_or_none()


class TaskRepository(BaseRepository):
    model = Task

    async def get_task_by_status(self, status_slug: str):
        result = await self.db.execute(
            select(self.model)
            .join(self.model.status)
            .where(TaskStatus.slug == status_slug)
            )
        return result.scalars().all()

    async def get_task_by_priority(self, priority_slug: str):
        result = await self.db.execute(
            select(self.model)
            .join(self.model.priority)
            .where(Priority.slug == priority_slug)
            )
        return result.scalars().all()
