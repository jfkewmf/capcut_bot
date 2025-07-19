# keyboards/reply/admin.py faylida
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Shablon qo'shish ➕")]
    ],
    resize_keyboard=True
)

cancel_markup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Bekor qilish ❌")]
    ],
    resize_keyboard=True
)

cancel_skip_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Bekor qilish ❌"),
            KeyboardButton(text="O‘tkazib yuborish ⏭️")
        ]
    ],
    resize_keyboard=True
)