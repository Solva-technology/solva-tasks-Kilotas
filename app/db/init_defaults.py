from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models.user import User, UserRole
from app.db.models.groups import Group


async def init_test_data():
    async with AsyncSessionLocal() as session:
        for role_name in ["student", "teacher"]:
            res = await session.execute(select(User).where(User.role == role_name))
            user = res.scalar_one_or_none()
            if not user:
                session.add(
                    User(
                        telegram_id=f"test_{role_name}_id",
                        username=f"{role_name}_user",
                        full_name=f"Test {role_name.capitalize()}",
                        role=UserRole(role_name),
                    )
                )

        res = await session.execute(select(Group).where(Group.name == "Test Group"))
        group = res.scalar_one_or_none()
        if not group:
            session.add(Group(name="Test Group"))

        await session.commit()
