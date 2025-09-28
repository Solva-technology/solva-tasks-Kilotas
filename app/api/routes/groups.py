import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.models.groups import Group
from app.db.models.user import User
from app.deps.roles import require_teacher_or_admin
from app.schemas.groups import GroupCreate, GroupOut, GroupDetail
from app.core.constants import GROUP_NOT_FOUND, STUDENT_NOT_FOUND

router = APIRouter(prefix="/groups", tags=["groups"])
log = logging.getLogger(__name__)


@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
async def create_group(
    data: GroupCreate,
    actor: User = Depends(require_teacher_or_admin),
    session: AsyncSession = Depends(get_session),
):
    group = Group(name=data.name, manager_id=data.manager_id)
    session.add(group)
    await session.commit()
    await session.refresh(group)

    log.info(
        {
            "action": "group_created",
            "user_id": actor.id,
            "group_id": group.id,
            "name": group.name,
            "manager_id": group.manager_id,
        }
    )

    return GroupOut(id=group.id, name=group.name, manager_id=group.manager_id)


@router.get("/", response_model=list[GroupOut])
async def list_groups(
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Group).order_by(Group.id))
    groups = res.scalars().all()
    return [GroupOut(id=g.id, name=g.name, manager_id=g.manager_id) for g in groups]


@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(
    group_id: int,
    session: AsyncSession = Depends(get_session),
):
    group = (
        await session.execute(select(Group).where(Group.id == group_id))
    ).scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=GROUP_NOT_FOUND
        )

    return GroupDetail(
        id=group.id,
        name=group.name,
        manager_id=group.manager_id,
        students=[s.id for s in group.students],
    )


@router.post("/{group_id}/add_student", response_model=GroupDetail)
async def add_student_to_group(
    group_id: int,
    student_id: int,
    actor: User = Depends(require_teacher_or_admin),
    session: AsyncSession = Depends(get_session),
):
    group = (
        await session.execute(select(Group).where(Group.id == group_id))
    ).scalar_one_or_none()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=GROUP_NOT_FOUND
        )

    student = (
        await session.execute(select(User).where(User.id == student_id))
    ).scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=STUDENT_NOT_FOUND
        )

    group.students.append(student)
    await session.commit()
    await session.refresh(group)

    log.info(
        {
            "action": "student_added_to_group",
            "actor_id": actor.id,
            "group_id": group.id,
            "student_id": student.id,
        }
    )

    return GroupDetail(
        id=group.id,
        name=group.name,
        manager_id=group.manager_id,
        students=[s.id for s in group.students],
    )
