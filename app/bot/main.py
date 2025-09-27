import re, asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from app.bot.handlers import basic, tasks

BOT_TOKEN = "8078022129:AAHDt3NFMZtvUawb8CQyp14H7CWYfpjg_BA"


print("BOT_TOKEN len:", len(BOT_TOKEN), "preview:", (BOT_TOKEN[:5] + "...") if BOT_TOKEN else "<empty>")
if not re.match(r"^\d+:[A-Za-z0-9_-]{20,}$", BOT_TOKEN):
    raise RuntimeError("BOT_TOKEN отсутствует или формат неверен.")


bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(basic.router)
dp.include_router(tasks.router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
