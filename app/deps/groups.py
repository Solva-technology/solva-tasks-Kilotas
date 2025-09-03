from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.groups import Group
from app.db.models.user import User, UserRole


async def manager_group_ids(session: AsyncSession, user: User) -> list[int]:
    if user.role != UserRole.manager:
        return []
    res = await session.execute(select(Group.id).where(Group.manager_id == user.id))
    return [row[0] for row in res.all()]