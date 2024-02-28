from typing import Optional

from aiogram.filters.callback_data import CallbackData

# All parameters are optional, otherwide Pydantic error will be raised, if one of the parameters is not provided
class BookingCallbackFactory(CallbackData, prefix='booking'):
    date: Optional[str] = None
    room_name: Optional[str] = None
    desk_name: Optional[str] = None