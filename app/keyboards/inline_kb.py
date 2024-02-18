from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

num_days = 5

def create_inline_kb(width: int,
                     last_btn: str | None = None,
                     ) -> InlineKeyboardMarkup:

    # Initialize builder
    kb_builder = InlineKeyboardBuilder()

    # Initialize list of buttons
    buttons: list[InlineKeyboardButton] = []

    # Fill the list of buttons with args and kwargs
    for date in range(num_days):
        buttons.append(InlineKeyboardButton(
            text=(datetime.today() + timedelta(days=date)).date().strftime("%Y-%m-%d (%a)"),
            callback_data=f"{date}"
        ))

    # Unpack the list of buttons into builder with method row with parameter width
    kb_builder.row(*buttons, width=width)
    
    # Add the last button if it exists
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=last_btn,
            callback_data='last_btn'
            )
        )

    # Return the keyboard as an object of class InlineKeyboardMarkup
    return kb_builder.as_markup()