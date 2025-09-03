import enum
from datetime import datetime
from sqlalchemy import String, Text, Enum, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class TaskStatus(str, enum.Enum):
    NEW = "новая"
    IN_PROGRESS = "в работе"
    SUBMITTED = "сдана"
    ACCEPTED = "принята"


class Task(TimestampMixin, Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.NEW, nullable=False)

    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)

    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # связи (если хочешь)
    student = relationship("User", foreign_keys=[student_id])
    group = relationship("Group", foreign_keys=[group_id])
