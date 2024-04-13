from aiogram import Router
from dialogs.booking.dialogs import booking_dialog
from dialogs.cancel_bookings.dialogs import cancel_bookings_dialog
from dialogs.all_bookings.dialogs import all_bookings_dialog
from dialogs.desk.dialogs import desk_dialog

def register_dialogs(router: Router):
    # List of all dialog modules
    dialogs = [
        booking_dialog,
        cancel_bookings_dialog,
        all_bookings_dialog,
        desk_dialog,
    ]
    # Use include_routers to add all dialogs at once
    router.include_routers(*dialogs)