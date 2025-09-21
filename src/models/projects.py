from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from .base_models import BaseModel
from schemas.projects import InvitationStatus


class Project(BaseModel):
    title: Mapped[str] = mapped_column(String(256), nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id]
    )

    participating_users: Mapped[List["User"]] = relationship(
        secondary="project_participants",
        back_populates="participants_projects",
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        foreign_keys="Task.project_id"
    )
    invitations: Mapped[List["ProjectInvitation"]] = relationship(
        "ProjectInvitation",
        back_populates="project",
        foreign_keys="ProjectInvitation.project_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Project(id={self.id}, title={self.title})>"


class ProjectInvitation(BaseModel):
    status: Mapped[str] = mapped_column(String(256), default=InvitationStatus.PENDING)
    invited_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)

    invited: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_id], back_populates="project_invitations"
    )
    inviter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[inviter_id],
        back_populates="sent_invitations"

    )
    project: Mapped["Project"] = relationship(
        "Project",
        foreign_keys=[project_id],
        back_populates="invitations"
    )
