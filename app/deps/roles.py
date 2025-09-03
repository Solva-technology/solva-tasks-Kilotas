from fastapi import Depends, HTTPException, status
from app.deps.auth import get_current_user
from app.db.models.user import User, UserRole


def require_teacher_or_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in (UserRole.teacher, UserRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user


def require_admin_or_teacher_or_manager(user: User = Depends(get_current_user)) -> User:
    if user.role not in (UserRole.admin, UserRole.teacher, UserRole.manager):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user




