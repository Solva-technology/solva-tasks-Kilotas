from pydantic import BaseModel, Field
from typing import Optional, List


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    manager_id: Optional[int] = None


class GroupOut(BaseModel):
    id: int
    name: str
    manager_id: int | None

    class Config:
        from_attributes = True


class GroupDetail(GroupOut):
    students: List[int]


class AddStudentIn(BaseModel):
    student_id: int
