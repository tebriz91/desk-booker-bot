from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_delete_booking_by_id
from states.states import CancelBookings

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner


async def selected_booking(query: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str,
                        ) -> None:
    """
    Handle the selection of a booking in the cancel bookings dialog.
    
    item_id (str): The selected booking_id.
    """
    # Get TranslatorRunner from i18n middleware
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    # Get session from DataBaseSession middleware
    session: AsyncSession = dialog_manager.middleware_data['session']
    # Get the selected booking_id
    booking_id = int(item_id)
    await orm_delete_booking_by_id(session, booking_id)
    await query.answer(text=i18n.cancel.booking.success())
    await dialog_manager.switch_to(state=CancelBookings.select_booking)