import datetime

from typing import List
from slugify import slugify

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Text

from .base_models import BaseModel


class TaskStatus(BaseModel):
    __tablename__ = "task_statuses"

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    slug: Mapped[str] = mapped_column(nullable=True)
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="status",
        foreign_keys="Task.status_id"
    )

    def __init__(self, **kw):
        super().__init__(**kw)
        if not self.slug and self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f"<TaskStatus(id={self.id}, title={self.title})>"


class Priority(BaseModel):
    __tablename__ = "priorities"

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    slug: Mapped[str] = mapped_column(nullable=True)
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="priority",
        foreign_keys="Task.priority_id"
    )

    def __init__(self, **kw):
        super().__init__(**kw)
        if not self.slug and self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f"<Priority(id={self.id}, title={self.title})>"


class Task(BaseModel):
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime.datetime] = mapped_column(nullable=False, index=True)

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    performer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("task_statuses.id"), index=True)
    priority_id: Mapped[int] = mapped_column(ForeignKey("priorities.id"), index=True)

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks"
    )
    performer: Mapped["User"] = relationship(
        "User",
        back_populates="performers"
    )
    status: Mapped["TaskStatus"] = relationship(
        "TaskStatus",
        back_populates="tasks"
    )
    priority: Mapped["Priority"] = relationship(
        "Priority",
        back_populates="tasks"
    )

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title})>"
