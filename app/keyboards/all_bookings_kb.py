from typing import List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callbacks import CBFAllBookings
from keyboards.utils.callback_btns import get_callback_util_btns

#* Room's inline keyboard
def create_kb_with_room_names(
    rooms: list,
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
    
    for room in rooms:
        buttons.append(InlineKeyboardButton(
            text=room,
            callback_data=CBFAllBookings(room_name=room).pack()
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