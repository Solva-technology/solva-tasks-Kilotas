# app/bot/bot.py
import re, asyncio, httpx
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

# Вставляем токены напрямую
BOT_TOKEN = "8078022129:AAHDt3NFMZtvUawb8CQyp14H7CWYfpjg_BA"
BOT_SECRET = "super-strong-random-secret"
BACKEND_URL = "http://127.0.0.1:8000"


print("BOT_TOKEN len:", len(BOT_TOKEN), "preview:", (BOT_TOKEN[:5] + "...") if BOT_TOKEN else "<empty>")
if not re.match(r"^\d+:[A-Za-z0-9_-]{20,}$", BOT_TOKEN):
    raise RuntimeError("BOT_TOKEN отсутствует или формат неверен.")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def on_start(message: Message):
    telegram_id = str(message.chat.id)
    username = message.from_user.username or ""
    full_name = (message.from_user.full_name or "").strip()

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{BACKEND_URL}/auth/telegram/callback",
            headers={"X-Bot-Secret": BOT_SECRET, "Content-Type": "application/json"},
            json={"telegram_id": telegram_id, "username": username, "full_name": full_name},
        )
    await message.answer("Вы успешно авторизованы ✅." if r.status_code == 200 else f"Ошибка: {r.status_code} {r.text}")

@dp.message(F.text)
async def echo(message: Message):
    await message.answer("Я бот задач. Напишите /start для авторизации.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())