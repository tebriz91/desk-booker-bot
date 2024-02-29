from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.callbacks import CBFUtilButtons

def get_callback_btns_back_and_cancel(
    *,
    back_btn: str,
    cancel_btn: str,
    sizes: tuple[int] = (2,)
    ):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=back_btn,
            callback_data=CBFUtilButtons(action=back_btn).pack()
        ),
        InlineKeyboardButton(
            text=cancel_btn,
            callback_data=CBFUtilButtons(action=cancel_btn).pack()
        )
    )
    return keyboard.adjust(*sizes).as_markup()

def get_callback_btn_cancel(
    *,
    cancel_btn: str,
    sizes: tuple[int] = (2,)
    ):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=cancel_btn,
            callback_data=cancel_btn
        )
    )
    return keyboard.adjust(*sizes).as_markup()

def get_callback_btn_back(
    *,
    back_btn: str,
    sizes: tuple[int] = (2,)
    ):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=back_btn,
            callback_data=back_btn
        )
    )
    return keyboard.adjust(*sizes).as_markup()