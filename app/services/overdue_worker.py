import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_

from app.db.session import AsyncSessionLocal
from app.db.models.task import Task, TaskStatus
from app.db.models.groups import Group
from app.db.models.user import User
from app.services.notifier import send_tg_message
from app.services.redis_client import get_redis

log = logging.getLogger(__name__)

SLEEP_SEC = 6000
REDIS_TTL = 24 * 60 * 60


async def overdue_worker():
    log.info("🚀 Воркер запущен!")
    try:
        while True:
            try:
                log.info("🔍 Начинаю проверку просроченных задач...")
                now = datetime.now(timezone.utc)

                async with AsyncSessionLocal() as session:
                    conds = [
                        Task.deadline.is_not(None),
                        Task.deadline < now,
                        Task.status != TaskStatus.ACCEPTED,
                    ]
                    res = await session.execute(select(Task).where(and_(*conds)))
                    tasks = res.scalars().all()

                if not tasks:
                    # Точка отмены (shutdown отменит этот sleep) — это норм
                    await asyncio.sleep(SLEEP_SEC)
                    continue

                redis = await get_redis()

                for t in tasks:
                    key = f"overdue:{t.id}"

                    ok = await redis.set(key, "1", ex=REDIS_TTL, nx=True)
                    if not ok:
                        continue

                    async with AsyncSessionLocal() as session:
                        stu = (await session.execute(
                            select(User).where(User.id == t.student_id)
                        )).scalar_one_or_none()
                        grp = (await session.execute(
                            select(Group).where(Group.id == t.group_id)
                        )).scalar_one_or_none()
                        mgr = None
                        if grp and grp.manager_id:
                            mgr = (await session.execute(
                                select(User).where(User.id == grp.manager_id)
                            )).scalar_one_or_none()

                    student_text = (
                        "⏰ <b>Дедлайн прошёл</b>\n"
                        f"<b>{t.title}</b>\n"
                        f"Статус: {t.status}\n"
                        f"Дедлайн: {t.deadline or '—'}\n\n"
                        "Пожалуйста, обновите статус или свяжитесь с преподавателем."
                    )
                    manager_text = (
                        "🔔 <b>Просроченная задача</b>\n"
                        f"<b>{t.title}</b>\n"
                        f"Студент: {stu.full_name or stu.username or stu.id if stu else '—'}\n"
                        f"Статус: {t.status}\n"
                        f"Дедлайн: {t.deadline or '—'}"
                    )

                    # не даём одному падению сломать цикл
                    try:
                        if stu and stu.telegram_id:
                            await send_tg_message(stu.telegram_id, student_text)
                        if mgr and mgr.telegram_id:
                            await send_tg_message(mgr.telegram_id, manager_text)
                        log.info({"overdue_notified": True, "task_id": t.id})
                    except Exception:
                        log.exception({"overdue_notify_failed": True, "task_id": t.id})

            except Exception:
                log.exception("overdue_worker iteration error")

            # Вторая точка сна/отмены после обработки пачки
            await asyncio.sleep(SLEEP_SEC)

    except asyncio.CancelledError:
        log.debug("overdue_worker cancelled")
        return

