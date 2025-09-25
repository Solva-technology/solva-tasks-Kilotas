# app/api/routes/debug.py (фрагмент)
from fastapi import APIRouter
from app.services.overdue_worker import overdue_worker

router = APIRouter(prefix="/debug", tags=["debug"])

@router.post("/overdue_once")
async def run_overdue_once():
    # выполняем один цикл без вечного while: переиспользуем логику внутри воркера
    # самый простой способ — временная обёртка:
    import asyncio
    async def one_shot():
        # вырезка из overdue_worker без sleep и while
        from datetime import datetime, timezone
        from sqlalchemy import select, and_
        from app.db.session import AsyncSessionLocal
        from app.db.models.task import Task, TaskStatus
        from app.db.models.groups import Group
        from app.db.models.user import User
        from app.services.notifier import send_tg_message
        from app.services.redis_client import get_redis

        now = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as session:
            conds = [Task.deadline.is_not(None), Task.deadline < now, Task.status != TaskStatus.ACCEPTED]
            res = await session.execute(select(Task).where(and_(*conds)))
            tasks = res.scalars().all()

        if not tasks:
            return {"sent": 0}

        redis = await get_redis()
        sent = 0
        for t in tasks:
            key = f"overdue:{t.id}"
            ok = await redis.set(key, "1", ex=24*60*60, nx=True)
            if not ok:
                continue
            async with AsyncSessionLocal() as session:
                stu = (await session.execute(select(User).where(User.id == t.student_id))).scalar_one_or_none()
                grp = (await session.execute(select(Group).where(Group.id == t.group_id))).scalar_one_or_none()
                mgr = None
                if grp and grp.manager_id:
                    mgr = (await session.execute(select(User).where(User.id == grp.manager_id))).scalar_one_or_none()
            if stu and stu.telegram_id:
                await send_tg_message(stu.telegram_id, f"⏰ Просрочено: {t.title}")
            if mgr and mgr.telegram_id:
                await send_tg_message(mgr.telegram_id, f"🔔 Просрочено у студента: {t.title}")
            sent += 1
        return {"sent": sent}

    return await one_shot()

