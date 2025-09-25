from app.db.base import Base

from .groups import Group
from .task import Task
from .user import User

__all__ = ["Base", "User", "Task", "Group"]
metadata = Base.metadata

