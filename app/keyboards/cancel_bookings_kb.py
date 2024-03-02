from typing import Dict, List, Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import Booking

from keyboards.callbacks import CBFCancelBooking
from keyboards.utils.callback_btns import get_callback_util_btns

def create_kb_with_bookings_to_cancel(
    bookings: Dict[Booking.id, str],
    width: int,
    util_buttons_order: List[str],
    util_buttons_width: int,
    cancel_btn: Optional[str] = None,
    back_btn: Optional[str] = None,
    next_btn: Optional[str] = None,
    exit_btn: Optional[str] = None,
    ok_btn: Optional[str] = None
    ) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    for booking_id, booking in bookings.items():
        buttons.append(InlineKeyboardButton(
            text=booking,
            callback_data=CBFCancelBooking(booking_id=booking_id).pack()
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