from sqlalchemy import (
Column, Integer, String, ForeignKey, Table, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base, TimestampMixin



user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "group_id", name="uq_user_group"),
    Index("ix_user_group_user_id", "user_id"),
    Index("ix_user_group_group_id", "group_id"),
)

class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)


    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    manager: Mapped["User"] = relationship(
        "User",
        foreign_keys=[manager_id],
        lazy="selectin",
    )

    students: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_group,
        back_populates="groups",
        lazy="selectin",
    )

    def __str__(self) -> str:
        return f"Group {self.name} (#{self.id})"

