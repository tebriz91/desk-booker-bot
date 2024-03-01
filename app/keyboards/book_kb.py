from typing import List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callbacks import CBFBook
from keyboards.utils.callback_btns import get_callback_util_btns

from services.dates_generator import generate_dates

#* Date's inline keyboard
def create_kb_with_dates(
    num_days: int,
    exclude_weekends: bool,
    timezone: str,
    country_code: str,
    date_format: str,
    width: int, # Width of the keyboard
    util_buttons_order: List[str],  # Add this parameter to specify the order of utility buttons
    util_buttons_width: int, # Width for utility buttons
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    cancel_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
    ) -> InlineKeyboardMarkup:
    '''
    Generate an inline keyboard with dates based on provided parameters.
    
    :param num_days: Number of days to generate.
    :param exclude_weekends: Whether to exclude weekends.
    :param timezone: Timezone.
    :param country_code: Country code.
    :param date_format: Date format.
    :param width: Width for keyboard with dates.
    :param util_buttons_order: Order of utility buttons.
    :param util_buttons_width: Width for utility buttons.
    :param back_btn: Text for the "Back" button. None if not needed.
    :param next_btn: Text for the "Next" button. None if not needed.
    :param cancel_btn: Text for the "Cancel" button. None if not needed.
    :param exit_btn: Text for the "Exit" button. None if not needed.
    :param ok_btn: Text for the "Ok" button. None if not needed.
    :return: An instance of InlineKeyboardMarkup.
    '''
    # Initialize builder
    keyboard = InlineKeyboardBuilder()

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
            callback_data=CBFBook(date=date).pack()
        ))

    # Unpack the list of buttons into builder with method row with parameter width
    keyboard.row(*buttons, width=width)
    
    # Get the utility buttons
    ordered_util_buttons = get_callback_util_btns(
    util_buttons_order=util_buttons_order,
    back_btn=back_btn,
    next_btn=next_btn,
    cancel_btn=cancel_btn,
    exit_btn=exit_btn,
    ok_btn=ok_btn
    )
    
    # Iterate over the utility buttons dictionary to add them to the the end of the keyboard
    util_buttons = [
        InlineKeyboardButton(
            text=btn_text,
            callback_data=callback_data)
        for btn_text, callback_data in ordered_util_buttons]
    
    keyboard.row(*util_buttons, width=util_buttons_width)

    # Return the keyboard as an object of class InlineKeyboardMarkup
    return keyboard.as_markup()

#* Room's inline keyboard
def create_kb_with_room_names(
    rooms: list,
    width: int,
    util_buttons_order: List[str],  # Add this parameter to specify the order of utility buttons
    util_buttons_width: int, # Width for utility buttons
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    cancel_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
    ) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for room in rooms:
        buttons.append(InlineKeyboardButton(
            text=room,
            callback_data=CBFBook(room_name=room).pack()
        ))
    
    keyboard.row(*buttons, width=width)
    
    ordered_util_buttons = get_callback_util_btns(
    util_buttons_order=util_buttons_order,
    back_btn=back_btn,
    next_btn=next_btn,
    cancel_btn=cancel_btn,
    exit_btn=exit_btn,
    ok_btn=ok_btn
    )

    util_buttons = [
        InlineKeyboardButton(
            text=btn_text,
            callback_data=callback_data)
        for btn_text, callback_data in ordered_util_buttons]
    
    keyboard.row(*util_buttons, width=util_buttons_width)
    
    return keyboard.as_markup()

#* Desk's inline keyboard
def create_kb_with_desk_names(
    desks: list,
    width: int, # Width of the keyboard
    util_buttons_order: List[str],  # Add this parameter to specify the order of utility buttons
    util_buttons_width: int, # Width for utility buttons
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    cancel_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
    ) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for desk in desks:
        buttons.append(InlineKeyboardButton(
            text=desk,
            callback_data=CBFBook(desk_name=desk).pack()
        ))
    
    keyboard.row(*buttons, width=width)
    
    ordered_util_buttons = get_callback_util_btns(
    util_buttons_order=util_buttons_order,
    back_btn=back_btn,
    next_btn=next_btn,
    cancel_btn=cancel_btn,
    exit_btn=exit_btn,
    ok_btn=ok_btn
    )

    util_buttons = [
        InlineKeyboardButton(
            text=btn_text,
            callback_data=callback_data)
        for btn_text, callback_data in ordered_util_buttons]
    
    keyboard.row(*util_buttons, width=util_buttons_width)

    return keyboard.as_markup()