from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

#* Admin's main relpy keyboard
def create_admin_kb(
    buttons: List[str],
    sizes: int = 2
    ) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    for button in buttons:
        keyboard.add(KeyboardButton(text=button))
    keyboard.adjust(sizes)
    return keyboard.as_markup(resize_keyboard=True)