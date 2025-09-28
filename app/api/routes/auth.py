import logging
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.db.models.user import User, UserRole
from app.db.session import get_session
from app.schemas.auth import TelegramAuthIn, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])
log = logging.getLogger(__name__)


@router.post("/telegram/callback", response_model=TokenOut)
async def telegram_callback(
    data: TelegramAuthIn,
    x_bot_secret: str = Header(alias="X-Bot-Secret"),
    session: AsyncSession = Depends(get_session),
):
    if x_bot_secret != (getattr(settings, "BOT_SECRET", None) or "my-bot-secret"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid bot secret"
        )

    result = await session.execute(
        select(User).where(User.telegram_id == data.telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=data.telegram_id,
            username=data.username,
            full_name=data.full_name,
            role=UserRole.student,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        log.info(
            {
                "action": "user_register",
                "user_id": user.id,
                "telegram_id": user.telegram_id,
            }
        )
    else:
        updated = False
        if data.username and data.username != user.username:
            user.username = data.username
            updated = True
        if data.full_name and data.full_name != user.full_name:
            user.full_name = data.full_name
            updated = True
        if updated:
            await session.commit()
        log.info({"action": "user_login", "user_id": user.id})

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenOut(
        access_token=token,
        role=user.role.value if hasattr(user.role, "value") else str(user.role),
        id=user.id,
    )
