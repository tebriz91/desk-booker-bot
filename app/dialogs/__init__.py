from aiogram import Router
from app.dialogs.booking.dialogs import booking_dialog
from app.dialogs.cancel_bookings.dialogs import cancel_bookings_dialog
from app.dialogs.all_bookings.dialogs import all_bookings_dialog
from app.dialogs.desk.dialogs import desk_dialog
from app.dialogs.team.dialogs import team_dialog

def register_dialogs(router: Router):
    # List of all dialog modules
    dialogs = [
        booking_dialog,
        cancel_bookings_dialog,
        all_bookings_dialog,
        desk_dialog,
        team_dialog,
    ]
    # Use include_routers to add all dialogs at once
    router.include_routers(*dialogs)