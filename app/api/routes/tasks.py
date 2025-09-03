import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.db.models.user import User, UserRole
from app.db.models.groups import Group
from app.db.models.task import Task, TaskStatus
from app.deps.groups import manager_group_ids
from app.deps.roles import require_teacher_or_admin, require_admin_or_teacher_or_manager
from app.deps.auth import get_current_user
from app.schemas.tasks import TaskCreate, TaskOut, TaskDetail, TaskUpdate, TaskStatusUpdate
from app.services.notifier import send_tg_message

router = APIRouter(prefix="/tasks", tags=["tasks"])
log = logging.getLogger(__name__)

def to_out(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id, title=t.title, status=t.status,
        student_id=t.student_id, group_id=t.group_id, deadline=t.deadline
    )

@router.post("/", response_model=TaskOut, status_code=201)
async def create_task(
    data: TaskCreate,
    actor: User = Depends(require_teacher_or_admin),
    session: AsyncSession = Depends(get_session),
):
    # проверим наличие студента и группы
    stu = (await session.execute(select(User).where(User.id == data.student_id))).scalar_one_or_none()
    if not stu:
        raise HTTPException(status_code=404, detail="Student not found")
    grp = (await session.execute(select(Group).where(Group.id == data.group_id))).scalar_one_or_none()
    if not grp:
        raise HTTPException(status_code=404, detail="Group not found")

    task = Task(
        title=data.title,
        description=data.description,
        student_id=data.student_id,
        group_id=data.group_id,
        deadline=data.deadline,
        status=TaskStatus.NEW,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Лог
    log.info({
        "action": "task_created", "user_id": actor.id, "task_id": task.id,
        "student_id": task.student_id, "group_id": task.group_id, "title": task.title
    })

    # Уведомление студенту
    if stu.telegram_id:
        await send_tg_message(
            chat_id=stu.telegram_id,
            text=f"📌 <b>Новая задача</b>\n<b>{task.title}</b>\nСтатус: {task.status}\nДедлайн: {task.deadline or '—'}"
        )

    return to_out(task)


@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    actor: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    student_id: int | None = Query(default=None),
    group_id: int | None = Query(default=None),
    status_: TaskStatus | None = Query(default=None, alias="status"),
):
    conds = []
    # базовые фильтры из query
    if student_id is not None:
        conds.append(Task.student_id == student_id)
    if group_id is not None:
        conds.append(Task.group_id == group_id)
    if status_ is not None:
        conds.append(Task.status == status_)

    # ограничение по роли
    if actor.role == UserRole.manager:
        mgids = await manager_group_ids(session, actor)
        if not mgids:
            return []
        conds.append(Task.group_id.in_(mgids))
    elif actor.role == UserRole.student:
        # студент видит только свои задачи
        conds.append(Task.student_id == actor.id)
    else:
        # admin/teacher — без доп. ограничений
        pass

    stmt = select(Task)
    if conds:
        from sqlalchemy import and_
        stmt = stmt.where(and_(*conds))
    res = await session.execute(stmt.order_by(Task.id))
    return [to_out(t) for t in res.scalars().all()]

@router.get("/{task_id}", response_model=TaskDetail)
async def get_task(
    task_id: int,
    actor: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    # ограничения видимости
    if actor.role == UserRole.student and t.student_id != actor.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if actor.role == UserRole.manager:
        mgids = await manager_group_ids(session, actor)
        if t.group_id not in mgids:
            raise HTTPException(status_code=403, detail="Forbidden")

    return TaskDetail(
        **to_out(t).model_dump(),
        description=t.description,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )

@router.patch("/{task_id}", response_model=TaskDetail)
async def patch_task(
    task_id: int,
    data: TaskUpdate,
    actor: User = Depends(require_teacher_or_admin),
    session: AsyncSession = Depends(get_session),
):
    t = (await session.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    old_status = t.status

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(t, field, value)

    await session.commit()
    await session.refresh(t)

    log.info({
        "action": "task_updated", "user_id": actor.id, "task_id": t.id,
        "old_status": old_status, "new_status": t.status
    })

    return TaskDetail(
        **to_out(t).model_dump(),
        description=t.description,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )

@router.patch("/{task_id}/status", response_model=TaskDetail)
async def student_change_status(
    task_id: int,
    data: TaskStatusUpdate,
    actor: User = Depends(get_current_user),  # студент сам
    session: AsyncSession = Depends(get_session),
):
    # найдём задачу, убедимся, что она его
    t = (await session.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    if actor.role == UserRole.student and t.student_id != actor.id:
        raise HTTPException(status_code=403, detail="Not your task")

    old_status = t.status
    t.status = data.status
    await session.commit()
    await session.refresh(t)

    log.info({
        "action": "task_status_changed", "user_id": actor.id, "task_id": t.id,
        "old_status": old_status, "new_status": t.status
    })

    # уведомление менеджеру группы
    grp = (await session.execute(select(Group).where(Group.id == t.group_id))).scalar_one_or_none()
    if grp and grp.manager_id:
        mgr = (await session.execute(select(User).where(User.id == grp.manager_id))).scalar_one_or_none()
        if mgr and mgr.telegram_id:
            await send_tg_message(
                chat_id=mgr.telegram_id,
                text=f"🔔 Статус задачи у студента {actor.full_name or actor.username or actor.id} изменён: "
                     f"<b>{t.title}</b>\n{old_status} → <b>{t.status}</b>"
            )

    return TaskDetail(
        **to_out(t).model_dump(),
        description=t.description,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


