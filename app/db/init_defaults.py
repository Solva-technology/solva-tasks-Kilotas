from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import UserRole


async def init_defaults():
    async with AsyncSessionLocal() as session:
        for role_name in ["student", "teacher"]:
            res = await session.execute(
                select(UserRole).where(UserRole.name == role_name)
            )
            role = res.scalar_one_or_none()
            if not role:
                session.add(UserRole(name=role_name))
        await session.commit()

