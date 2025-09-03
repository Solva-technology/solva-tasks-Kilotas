from datetime import datetime
from pydantic import BaseModel
from app.db.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    student_id: int
    group_id: int
    deadline: datetime | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    status: TaskStatus
    student_id: int
    group_id: int
    deadline: datetime | None


class TaskDetail(TaskOut):
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    student_id: int | None = None
    group_id: int | None = None
    deadline: datetime | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus