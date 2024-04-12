from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram.types import CallbackQuery

from sqlalchemy.ext.asyncio import AsyncSession

from states.states import AllBookings

from services.common.room_plan_getter import get_room_plan_by_room_id
from services.bookings_list_generator import AllBookingsError, generate_current_bookings_list_by_room_id

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger
logger = Logger()


async def selected_room(query: CallbackQuery,
                        widget: Select,
                        dialog_manager: DialogManager,
                        item_id: str,
                        ) -> None:
    # Get TranslatorRunner from i18n middleware
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    # Get session from DataBaseSession middleware
    session: AsyncSession = dialog_manager.middleware_data['session']
    # Save the selected room_id to the dialog data
    dialog_manager.dialog_data['room_id'] = int(item_id)
    # Get the bot operation configuration
    c = dialog_manager.start_data['bot_operation_config']
    # Get room_plan from the database
    room_plan_url = await get_room_plan_by_room_id(
        session,
        room_id=int(item_id))
    # Save room_plan_url to the dialog data
    dialog_manager.dialog_data['room_plan_url'] = room_plan_url
    
    try:
        bookings = await generate_current_bookings_list_by_room_id(
            i18n,
            session,
            date_format=c['date_format'],
            date_format_short=c['date_format_short'],
            room_id=int(item_id),
        )
        dialog_manager.dialog_data['bookings'] = bookings
        await dialog_manager.switch_to(AllBookings.view_bookings)
    except AllBookingsError as no_bookings:
        await query.answer(text=f'{no_bookings}', show_alert=True)
        await dialog_manager.switch_to(state=AllBookings.select_room)
    except Exception as e:
        await query.answer(text=str(e), show_alert=True)
        await dialog_manager.done()