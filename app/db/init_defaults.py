# app/db/init_defaults.py
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import User, UserRole
from app.db.models.groups import Group


async def init_defaults():
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(User).where(User.role == UserRole.teacher)
        )
        teacher = res.scalar_one_or_none()

        if not teacher:
            teacher = User(
                telegram_id="init_teacher",
                username="init_teacher",
                full_name="Default Teacher",
                role=UserRole.teacher,
            )
            session.add(teacher)
            await session.flush()


        res = await session.execute(select(Group))
        group = res.scalar_one_or_none()

        if not group:
            group = Group(
                name="Default Group",
                manager_id=teacher.id,
            )
            session.add(group)

        await session.commit()
