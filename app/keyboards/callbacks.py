from typing import Optional

from aiogram.filters.callback_data import CallbackData

# All parameters are optional, otherwide Pydantic error will be raised, if one of the parameters is not provided
class CBFBook(CallbackData, prefix='book'):
    date: Optional[str] = None
    room_name: Optional[str] = None
    desk_name: Optional[str] = None

class CBFAllBookings(CallbackData, prefix='all_bookings'):
    room_name: Optional[str] = None

class CBFCancelBooking(CallbackData, prefix='cancel_booking'):
    booking_id: Optional[int] = None #TODO: check callback parameter
    
class CBFUtilButtons(CallbackData, prefix='util_buttons'):
    action: Optional[str] = None