from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from .base_models import BaseModel


class Project(BaseModel):
    title: Mapped[str] = mapped_column(String(256), nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id]
    )

    participants: Mapped[List["User"]] = relationship(
        secondary="project_participants",
        back_populates="participating_projects"
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        foreign_keys="Task.project_id"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title})>"
