from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from app.bot.api import api_post
from app.bot.keyboards import main_keyboard
from app.bot.state import TOKENS

router = Router()
BOT_SECRET = "super-strong-random-secret"


@router.message(CommandStart())
async def on_start(message: Message):
    telegram_id = str(message.chat.id)
    username = message.from_user.username or ""
    full_name = (message.from_user.full_name or "").strip()

    r = await api_post(
        "/auth/telegram/callback",
        json={"telegram_id": telegram_id, "username": username, "full_name": full_name},
        headers={"X-Bot-Secret": BOT_SECRET},
    )
    if r.status_code == 200:
        data = r.json()
        token = data.get("access_token") or data.get("token")
        if not token:
            await message.answer(
                "Авторизация прошла, но сервер не вернул токен.",
                reply_markup=main_keyboard,
            )
            return
        TOKENS[telegram_id] = token
        await message.answer(
            "Вы успешно авторизованы ✅\n\nИспользуйте кнопки ниже:",
            reply_markup=main_keyboard,
        )
    else:
        await message.answer(
            f"Ошибка авторизации: {r.status_code}\n{r.text}", reply_markup=main_keyboard
        )


@router.message(F.text.func(lambda s: s and "статус" in s.lower()))
async def statuses_help(message: Message):
    await message.answer(
        "Доступные статусы:\n"
        "• NEW — новая\n"
        "• IN_PROGRESS — в работе\n"
        "• SUBMITTED — сдана на проверку\n"
        "• ACCEPTED — принята\n\n"
        "Чтобы поменять, откройте задачу: /task &lt;id&gt; и нажмите кнопку.\n"
        "Например: <code>/task 58</code>"
    )


@router.message(F.text.func(lambda s: s and "помощ" in s.lower()))
async def help_button(message: Message):
    await message.answer(
        "Команды:\n"
        "• /start — авторизация\n"
        "• /my — мои задачи\n"
        "• /task &lt;id&gt; — детали + кнопки статуса"
    )
