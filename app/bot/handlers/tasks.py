from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.bot.api import api_get, api_patch
from app.bot.keyboards import main_keyboard, status_keyboard
from app.bot.state import TOKENS

router = Router()


@router.message(F.text == "📋 Мои задачи")
async def my_tasks_button(message: Message):
    await my_tasks(message)


@router.message(Command("my"))
async def my_tasks(message: Message):
    chat_id = str(message.chat.id)
    token = TOKENS.get(chat_id)
    if not token:
        await message.answer(
            "Сначала нажмите /start для авторизации.", reply_markup=main_keyboard
        )
        return

    r = await api_get("/tasks/my", token=token)
    if r.status_code != 200:
        await message.answer(f"❌ Ошибка запроса: {r.status_code}\n{r.text}")
        return

    tasks = r.json()
    if not tasks:
        await message.answer("Пока задач нет ✨")
        return

    lines = []
    for t in tasks[:20]:
        dl = t.get("deadline")
        if dl:
            try:
                dl_str = datetime.fromisoformat(dl.replace("Z", "+00:00")).strftime(
                    "%Y-%m-%d %H:%M"
                )
            except:
                dl_str = dl
        else:
            dl_str = "—"
        lines.append(
            f"<b>#{t['id']}</b> • {t['title']}\nСтатус: <code>{t['status']}</code> • Дедлайн: {dl_str}"
        )
    await message.answer("📋 <b>Мои задачи</b>\n\n" + "\n\n".join(lines))


@router.message(Command("task"))
async def task_detail(message: Message):
    chat_id = str(message.chat.id)
    token = TOKENS.get(chat_id)
    if not token:
        await message.answer(
            "Сначала нажмите /start для авторизации.", reply_markup=main_keyboard
        )
        return

    parts = message.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Использование: <code>/task 123</code>")
        return
    task_id = int(parts[1])

    r = await api_get(f"/tasks/{task_id}", token=token)
    if r.status_code != 200:
        await message.answer(
            f"❌ Не удалось получить задачу #{task_id}: {r.status_code}\n{r.text}"
        )
        return

    t = r.json()
    dl = t.get("deadline")
    if dl:
        try:
            dl_str = datetime.fromisoformat(dl.replace("Z", "+00:00")).strftime(
                "%Y-%m-%d %H:%M"
            )
        except:
            dl_str = dl
    else:
        dl_str = "—"

    await message.answer(
        f"🗂 <b>#{t['id']} {t['title']}</b>\n"
        f"Статус: <code>{t['status']}</code>\n"
        f"Дедлайн: {dl_str}\n\n"
        f"{t.get('description') or ''}",
        reply_markup=status_keyboard(task_id),
    )


@router.callback_query(F.data.startswith("setstatus:"))
async def cb_setstatus(callback: CallbackQuery):
    chat_id = str(callback.from_user.id)
    token = TOKENS.get(chat_id)
    if not token:
        await callback.answer("Вы не авторизованы. Нажмите /start", show_alert=True)
        return

    try:
        _, task_id_str, new_status = callback.data.split(":")
        task_id = int(task_id_str)
    except Exception:
        await callback.answer("Некорректные данные кнопки.", show_alert=True)
        return

    r = await api_patch(
        f"/tasks/{task_id}/status", json={"status": new_status}, token=token
    )
    if r.status_code == 200:
        t = r.json()
        await callback.message.edit_text(
            f"🗂 <b>#{t['id']} {t['title']}</b>\n"
            f"✅ Новый статус: <code>{t['status']}</code>"
        )
        await callback.answer("Статус обновлён ✅")
    elif r.status_code == 403:
        await callback.answer("⛔ Это не ваша задача", show_alert=True)
    elif r.status_code == 404:
        await callback.answer("❓ Задача не найдена", show_alert=True)
    else:
        await callback.answer(f"Ошибка: {r.status_code}", show_alert=True)
