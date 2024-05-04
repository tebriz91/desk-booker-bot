from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram.types import CallbackQuery

from app.states.states import AllBookings


async def selected_room(query: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str,
                        ) -> None:
    dialog_manager.dialog_data['room_id'] = item_id
    await dialog_manager.switch_to(AllBookings.view_bookings)