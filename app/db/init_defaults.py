from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.groups import Group


async def init_defaults():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.role == "teacher")
        )
        teacher = result.scalar_one_or_none()

        if not teacher:
            teacher = User(
                telegram_id="init_teacher",
                username="init_teacher",
                full_name="Default Teacher",
                role="teacher",
            )
            session.add(teacher)
            await session.flush()


        result = await session.execute(select(Group))
        group = result.scalar_one_or_none()

        if not group:
            group = Group(
                title="Default Group",
                description="Auto-created group for tests",
                teacher_id=teacher.id if teacher else None,
            )
            session.add(group)

        await session.commit()