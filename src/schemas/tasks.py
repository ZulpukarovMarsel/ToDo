from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .users import UserResponseSchema


class TaskStatusSchema(BaseModel):
    id: int
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime


class PrioritySchema(BaseModel):
    id: int
    title: str
    slug: str
    created_at: datetime
    updated_at: datetime


class TaskAddSchema(BaseModel):
    title: Optional[str] = None
    owner: Optional[int] = None
    participants: Optional[List[int]] = []


class TaskSchema(BaseModel):
    id: int
    title: str
    text: str
    deadline: datetime

    performer: UserResponseSchema
    status: TaskStatusSchema
    priority: PrioritySchema

    created_at: datetime
    updated_at: datetime
