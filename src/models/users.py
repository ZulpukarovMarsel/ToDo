from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Table, Column, ForeignKey
from typing import List
from slugify import slugify

from schemas.users import UserSchema
from schemas.roles import RoleSchema
from .base_models import BaseModel


association_table = Table(
    "association_table",
    BaseModel.metadata,
    Column("roles_id", ForeignKey("roles.id")),
    Column("users_id", ForeignKey("users.id")),
)


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
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    image: Mapped[str] = mapped_column(nullable=True, default='')
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str] = mapped_column(nullable=False)
    roles: Mapped[List["Role"]] = relationship(
        secondary=association_table, back_populates="users"
    )

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    def to_read_model(self) -> UserSchema:
        return UserSchema(
            id=self.id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password,
            roles=[RoleSchema.model_validate(role) for role in self.roles]
        )
