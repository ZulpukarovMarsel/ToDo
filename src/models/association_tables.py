from sqlalchemy import Table, Column, ForeignKey
from .base_models import BaseModel

association_table = Table(
    "association_table",
    BaseModel.metadata,
    Column("roles_id", ForeignKey("roles.id")),
    Column("users_id", ForeignKey("users.id")),
)

project_participants = Table(
    "project_participants",
    BaseModel.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("project_id", ForeignKey("projects.id"))
)
