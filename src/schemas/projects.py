from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum
from .users import UserResponseSchema
from .tasks import TaskSchema


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class ProjectCreateSchema(BaseModel):
    title: Optional[str] = None


class ProjectCreateResponseSchema(BaseModel):
    id: int
    title: str
    owner: UserResponseSchema
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectResponseSchema(BaseModel):
    id: int
    title: str
    owner: UserResponseSchema
    participating_users: List[UserResponseSchema] = []
    tasks: List[TaskSchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectsResponseSchema(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class AddedInviterSchema(BaseModel):
    project_id: int
    invited_id: int

    model_config = ConfigDict(from_attributes=True)


class InvitationResponseSchema(BaseModel):
    id: int
    project_id: int
    invited_id: int
    inviter_id: int
    project: ProjectsResponseSchema
    invited: UserResponseSchema
    inviter: UserResponseSchema
    status: InvitationStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
