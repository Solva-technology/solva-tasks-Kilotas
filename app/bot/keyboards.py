from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

VALID_STATUSES = [
    ("новая", "NEW"),
    ("в работе", "IN_PROGRESS"),
    ("сдана", "SUBMITTED"),
    ("принята", "ACCEPTED"),
]

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Мои задачи"), KeyboardButton(text="📊 Статусы")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True
)


def status_keyboard(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for label, value in VALID_STATUSES:
        kb.add(
            InlineKeyboardButton(
                text=label.title(),
                callback_data=f"setstatus:{task_id}:{label}"
            )
        )
    kb.adjust(2)
    return kb.as_markup()

