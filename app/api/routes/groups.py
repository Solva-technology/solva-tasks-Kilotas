from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_session
from app.db.models import Group, User, user_group
from app.schemas.groups import GroupCreate, GroupOut, GroupDetail, AddStudentIn
from app.deps.roles import require_teacher_or_admin, require_admin_or_teacher_or_manager

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/", response_model=GroupOut)
async def create_group(
    data: GroupCreate,
    _: User = Depends(require_teacher_or_admin),
    session: AsyncSession = Depends(get_session),
):

    exists = await session.execute(select(Group).where(Group.name == data.name))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Group name already exists")

    group = Group(name=data.name, manager_id=data.manager_id)
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group


@router.get("/", response_model=list[GroupOut])
async def list_groups(
    _: User = Depends(require_admin_or_teacher_or_manager),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Group))
    return res.scalars().all()

@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(
    group_id: int,
    _: User = Depends(require_admin_or_teacher_or_manager),
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Group).where(Group.id == group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")


    res2 = await session.execute(
        select(User.id).join(user_group, user_group.c.user_id == User.id).where(user_group.c.group_id == group_id)
    )

    students = [row[0] for row in res2.all()]
    return GroupDetail(id=group.id, name=group.name, manager_id=group.manager_id, students=students)


@router.post("/{group_id}/add_student", response_model=GroupDetail)
async def add_student(
    group_id: int,
    data: AddStudentIn,
    _: User = Depends(require_teacher_or_admin),
    session: AsyncSession = Depends(get_session),
):

    gq = await session.execute(select(Group).where(Group.id == group_id))
    group = gq.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # студент существует и он student?
    uq = await session.execute(select(User).where(User.id == data.student_id))
    student = uq.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    exists = await session.execute(
        select(user_group).where(
            user_group.c.group_id == group_id, user_group.c.user_id == data.student_id
        )
    )
    if not exists.first():
        await session.execute(user_group.insert().values(group_id=group_id, user_id=data.student_id))
        await session.commit()

    res2 = await session.execute(
        select(User.id).join(user_group, user_group.c.user_id == User.id).where(user_group.c.group_id == group_id)
    )
    students = [row[0] for row in res2.all()]
    return GroupDetail(id=group.id, name=group.name, manager_id=group.manager_id, students=students)
