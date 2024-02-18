from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_buttons import LEXICON

# Function for creating inline-keyboard
def create_inline_kb(width: int,
                     *args: str,
                     last_btn: str | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:

    # Initialize builder
    kb_builder = InlineKeyboardBuilder()

    # Initialize list of buttons
    buttons: list[InlineKeyboardButton] = []

    # Fill the list of buttons with args and kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

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


def create_inline_kb_2(width: int,
                     *args: str,
                     last_btn: str | None = None,
                     **kwargs: str) -> InlineKeyboardMarkup:

    # Initialize builder
    kb_builder = InlineKeyboardBuilder()

    # Initialize list of buttons
    buttons: list[InlineKeyboardButton] = []

    # Fill the list of buttons with args and kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON[button] if button in LEXICON else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

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