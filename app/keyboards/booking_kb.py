from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.dates_generator import generate_dates

#* Date's inline keyboard
def create_kb_with_dates(
    num_days: int,
    exclude_weekends: bool,
    timezone: str,
    country_code: str,
    date_format: str,
    width: int, # Width of the keyboard
    last_btn: str | None = None, # Last button of the keyboard
    ) -> InlineKeyboardMarkup:

    # Initialize builder
    kb_builder = InlineKeyboardBuilder()

    # Initialize list of buttons
    buttons: list[InlineKeyboardButton] = []

    dates = generate_dates(
        num_days,
        exclude_weekends,
        timezone,
        country_code,
        date_format
    )
    
    # Fill the list of buttons with args and kwargs
    for date in dates:
        buttons.append(InlineKeyboardButton(
            text=(date if date else dates[date]),
            callback_data=date
        ))

    # Unpack the list of buttons into builder with method row with parameter width
    kb_builder.row(*buttons, width=width)
    
    # Add the last button if it exists
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=last_btn,
            callback_data='last_btn'
        ))

    # Return the keyboard as an object of class InlineKeyboardMarkup
    return kb_builder.as_markup()

#* Room's inline keyboard
def create_kb_with_room_names(
    rooms: list,
    width: int, # Width of the keyboard
    last_btn: str | None = None, # Last button of the keyboard
    ) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for room in rooms:
        buttons.append(InlineKeyboardButton(
            text=room,
            callback_data=room
        ))
    
    kb_builder.row(*buttons, width=width)
    
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=last_btn,
            callback_data='last_btn'
        ))

    return kb_builder.as_markup()

#* Desk's inline keyboard
def create_kb_with_desk_names(
    desks: list,
    width: int, # Width of the keyboard
    last_btn: str | None = None, # Last button of the keyboard
    ) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for desk in desks:
        buttons.append(InlineKeyboardButton(
            text=desk,
            callback_data=desk
        ))
    
    kb_builder.row(*buttons, width=width)
    
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=last_btn,
            callback_data='last_btn'
        ))

    return kb_builder.as_markup()