from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import (
    Select,
    Column,
    Cancel,
    Group,
)
from aiogram_dialog.widgets.text import Format

from states.states import CancelBookings

from dialogs.cancel_bookings.handlers import (
    selected_booking,
)
from dialogs.cancel_bookings.getters import (
    get_bookings,
)


cancel_bookings_dialog = Dialog(
    Window(
        Format(text='{no-bookings-to-cancel}',
               when='no-bookings-to-cancel'),
        Format(text='{cancel-booking-error}',
               when='cancel-booking-error'),
        Format(text='{select-booking-to-cancel}',
               when='bookings-to-cancel'),
        Group(
            Column(
                Select(
                    Format('{item[1]}'), # Booking data formatted as a string
                    id='booking_id',
                    items='bookings-to-cancel',
                    item_id_getter=lambda item: item[0], # Extract booking_id
                    on_click=selected_booking,
                ),
            ),
            Cancel(Format(text='{button-exit}')),
            when='bookings-to-cancel' # Display Group only when 'bookings-to-cancel' is not empty
        ),
        state=CancelBookings.select_booking,
        getter=get_bookings,
    ),
)