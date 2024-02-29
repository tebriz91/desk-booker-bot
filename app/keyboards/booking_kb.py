from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from enums.button_labels import ButtonLabel

from keyboards.callbacks import CBFBooking, CBFUtilButtons

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
            callback_data=CBFBooking(date=date).pack()
        ))

    # Unpack the list of buttons into builder with method row with parameter width
    kb_builder.row(*buttons, width=width)
    
    # Add the last button if it exists
    if last_btn:
        kb_builder.row(InlineKeyboardButton(
            text=last_btn,
            callback_data=CBFUtilButtons(action=ButtonLabel.CANCEL.value).pack()
        ))

    # Return the keyboard as an object of class InlineKeyboardMarkup
    return kb_builder.as_markup()

#* Room's inline keyboard
def create_kb_with_room_names(
    rooms: list,
    width: int, # Width of the keyboard
    last_btns: list[str, str] | None = None, # Last buttons of the keyboard
    ) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for room in rooms:
        buttons.append(InlineKeyboardButton(
            text=room,
            callback_data=CBFBooking(room_name=room).pack()
        ))
    
    kb_builder.row(*buttons, width=width)
    
    if last_btns:
        kb_builder.row(
            InlineKeyboardButton(
            text=last_btns[0],
            callback_data=CBFUtilButtons(action=ButtonLabel.BACK.value).pack()
        ),
            InlineKeyboardButton(
            text=last_btns[1],
            callback_data=CBFUtilButtons(action=ButtonLabel.CANCEL.value).pack()
        ))

    return kb_builder.as_markup()

#* Desk's inline keyboard
def create_kb_with_desk_names(
    desks: list,
    width: int, # Width of the keyboard
    last_btns: list[str, str] | None = None, # Last button of the keyboard
    ) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for desk in desks:
        buttons.append(InlineKeyboardButton(
            text=desk,
            callback_data=CBFBooking(desk_name=desk).pack()
        ))
    
    kb_builder.row(*buttons, width=width)
    
    if last_btns:
        kb_builder.row(
            InlineKeyboardButton(
            text=last_btns[0],
            callback_data=CBFUtilButtons(action=ButtonLabel.BACK.value).pack()
        ),
            InlineKeyboardButton(
            text=last_btns[1],
            callback_data=CBFUtilButtons(action=ButtonLabel.CANCEL.value).pack()
        ))

    return kb_builder.as_markup()

def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()