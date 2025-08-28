import enum
from sqlalchemy import String, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin  
from app.core.constants import TELEGRAM_ID_MAX_LEN, USERNAME_MAX_LEN, FULLNAME_MAX_LEN


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    manager = "manager"
    admin = "admin"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[str] = mapped_column(String(TELEGRAM_ID_MAX_LEN), unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(USERNAME_MAX_LEN))
    full_name: Mapped[str | None] = mapped_column(String(FULLNAME_MAX_LEN))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.student, nullable=False)