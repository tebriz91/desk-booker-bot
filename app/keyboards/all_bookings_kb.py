from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from enums.button_labels import ButtonLabel

from keyboards.callbacks import CBFAllBookings, CBFUtilButtons

#* Room's inline keyboard
def create_kb_with_room_names(
    rooms: list,
    width: int, # Width of the keyboard
    last_btn: str | None = None
    ) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []
    
    for room in rooms:
        buttons.append(InlineKeyboardButton(
            text=room,
            callback_data=CBFAllBookings(room_name=room).pack()
        ))
    
    kb_builder.row(*buttons, width=width)
    
    if last_btn:
        kb_builder.row(
            InlineKeyboardButton(
            text=last_btn,
            callback_data=CBFUtilButtons(action=ButtonLabel.CANCEL.value).pack()
        ))

    return kb_builder.as_markup()

def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()