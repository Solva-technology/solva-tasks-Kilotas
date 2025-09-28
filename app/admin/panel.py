from typing import Any
from starlette.requests import Request

from sqladmin import Admin, ModelView
from wtforms.validators import DataRequired

from app.db.session import engine, AsyncSessionLocal
from app.db.models.user import User
from app.db.models.groups import Group
from app.db.models.task import Task
from app.services.notifier import send_tg_message
import logging
from sqlalchemy import select

log = logging.getLogger(__name__)


def init_admin(app) -> Admin:
    admin = Admin(app, engine)

    class UserAdmin(ModelView, model=User):
        name_plural = "Users"
        column_list = [
            User.id,
            User.telegram_id,
            User.username,
            User.full_name,
            User.role,
            User.created_at,
        ]
        column_searchable_list = [User.username, User.full_name, User.telegram_id]
        column_sortable_list = [User.id, User.role, User.created_at]

    class GroupAdmin(ModelView, model=Group):
        name_plural = "Groups"
        column_list = [Group.id, Group.name, Group.manager_id, Group.created_at]
        column_searchable_list = [Group.name]
        column_sortable_list = [Group.id, Group.created_at]

    class TaskAdmin(ModelView, model=Task):
        name_plural = "Tasks"
        column_list = [
            Task.id,
            Task.title,
            Task.status,
            Task.student_id,
            Task.group_id,
            Task.deadline,
            Task.created_at,
        ]
        column_searchable_list = [Task.title]
        column_sortable_list = [Task.id, Task.status, Task.deadline, Task.created_at]

        form_columns = [
            Task.title,
            Task.description,
            Task.status,
            Task.student,
            Task.group,
            Task.deadline,
        ]

        form_ajax_refs = {
            "student": {"fields": (User.username, User.full_name, User.telegram_id)},
            "group": {"fields": (Group.name,)},
        }

        form_args = {
            "student": {"validators": [DataRequired(message="Select student")]},
            "group": {"validators": [DataRequired(message="Select group")]},
        }

        async def on_model_change(
            self, data: dict[str, Any], model: Task, is_created: bool, request: Request
        ) -> None:
            log.info(
                f"[BEFORE] created={is_created}, student_id={getattr(model,'student_id',None)}"
            )

        async def after_model_change(
            self, data: dict[str, Any], model: Task, is_created: bool, request: Request
        ) -> None:
            sid = getattr(model, "student_id", None)
            if not is_created:
                return

            if not sid:
                raw = data.get("student")
                if hasattr(raw, "id"):
                    sid = raw.id
                elif isinstance(raw, dict):
                    for k in ("id", "pk", "value"):
                        if k in raw:
                            try:
                                sid = int(raw[k])
                                break
                            except Exception:
                                pass
                elif isinstance(raw, (list, tuple)) and raw:
                    v = raw[0]
                    if isinstance(v, (int, str)) and str(v).isdigit():
                        sid = int(v)
                elif isinstance(raw, (int, str)) and str(raw).isdigit():
                    sid = int(raw)

            log.info({"hook": "after", "created": is_created, "sid": sid})
            if not sid:
                log.error(
                    {"hook": "no_sid_after_create", "data_keys": list(data.keys())}
                )
                return

            async with AsyncSessionLocal() as session:
                res = await session.execute(
                    select(User.telegram_id).where(User.id == sid)
                )
                chat_id = res.scalar_one_or_none()

            if not chat_id:
                log.error({"hook": "no_chat_id_for_sid", "sid": sid})
                return

            ok = await send_tg_message(
                chat_id,
                f"📌 <b>Новая задача</b>\n<b>{model.title}</b>\n"
                f"Статус: {model.status}\nДедлайн: {getattr(model, 'deadline', '—') or '—'}",
            )
            log.info({"hook": "notify_sent", "ok": ok, "sid": sid})

    admin.add_view(UserAdmin)
    admin.add_view(GroupAdmin)
    admin.add_view(TaskAdmin)

    return admin
