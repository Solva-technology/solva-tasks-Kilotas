# app/api/routes/debug.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.db.models.user import User
from app.services.notifier import send_tg_message
from app.deps.auth import get_current_user

router = APIRouter(prefix="/_debug", tags=["_debug"])

@router.post("/ping_tg/{user_id}")
async def ping_tg(user_id: int, _: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    u = (await session.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not u or not u.telegram_id:
        raise HTTPException(404, "user or telegram_id not found")
    ok = await send_tg_message(u.telegram_id, "🔧 Тестовое сообщение из API")
    return {"sent": ok}
