from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from slugify import slugify

from schemas.users import UserResponseSchema
from schemas.roles import RoleSchema
from .base_models import BaseModel
from .association_tables import association_table, project_participants


class Role(BaseModel):
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=True)
    users: Mapped[List["User"]] = relationship(
        secondary=association_table, back_populates="roles"
    )

    def __init__(self, **kw):
        super().__init__(**kw)
        if not self.slug and self.name:
            self.slug = slugify(self.name)

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"


class User(BaseModel):
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    image: Mapped[str] = mapped_column(nullable=True, default='')
    first_name: Mapped[str] = mapped_column(nullable=True, default='', index=True)
    last_name: Mapped[str] = mapped_column(nullable=True, default='', index=True)
    password: Mapped[str] = mapped_column(nullable=True, default='')
    roles: Mapped[List["Role"]] = relationship(
        secondary=association_table, back_populates="users"
    )
    owned_projects: Mapped[List['Project']] = relationship(
        "Project",
        back_populates="owner",
        foreign_keys="Project.owner_id"
    )
    participants_projects: Mapped[List['Project']] = relationship(
        secondary=project_participants,
        back_populates="participating_users"
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="performer",
        foreign_keys="Task.performer_id"
    )
    project_invitations: Mapped[List["ProjectInvitation"]] = relationship(
        "ProjectInvitation",
        foreign_keys="ProjectInvitation.invited_id",
        back_populates="invited",
        cascade="all, delete-orphan"
    )
    sent_invitations: Mapped[List["ProjectInvitation"]] = relationship(
        "ProjectInvitation",
        foreign_keys="ProjectInvitation.inviter_id",
        back_populates="inviter",
        cascade="all, delete-orphan"
    )

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
