from typing import Optional
from enums.button_labels import ButtonLabel

from aiogram.filters.callback_data import CallbackData

# All parameters are optional, otherwide Pydantic error will be raised, if one of the parameters is not provided
class CBFBooking(CallbackData, prefix='booking'):
    date: Optional[str] = None
    room_name: Optional[str] = None
    desk_name: Optional[str] = None

class CBFUtilButtons(CallbackData, prefix='util_buttons'):
    action: Optional[str] = None