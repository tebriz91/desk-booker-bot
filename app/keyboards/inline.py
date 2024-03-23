from typing import List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_inline_keyboard(
    buttons: Optional[List[str]] = None,
    width: int = 1,
    util_buttons: Optional[List[str]] = None,
    width_util: int = 2,
    ) -> InlineKeyboardMarkup:
    
    keyboard = InlineKeyboardBuilder()
    
    # Process main buttons
    if buttons:
        row: List[InlineKeyboardButton] = []
        for button_text in buttons:
            row.append(InlineKeyboardButton(
                text=button_text,
                callback_data=button_text
                ))
        keyboard.row(*row, width=width)
    
    # Process utility buttons
    if util_buttons:
        util_row: List[InlineKeyboardButton] = []
        for button_text in util_buttons:
            util_row.append(InlineKeyboardButton(
                text=button_text,
                callback_data=button_text
                ))
        keyboard.row(*util_row, width=width_util)
    
    return keyboard.as_markup()