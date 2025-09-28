from fastapi import APIRouter, Depends
from app.deps.auth import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
