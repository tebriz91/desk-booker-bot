from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram.types import CallbackQuery

from database.orm_queries import orm_switch_is_out_of_office_by_telegram_id_and_clear_bookings
from states.states import Desk


async def toggle_is_out_of_office_status(query: CallbackQuery,
                                         widget: Select,
                                         dialog_manager: DialogManager,
                                         ) -> None:
    session: AsyncSession = dialog_manager.middleware_data['session']
    await orm_switch_is_out_of_office_by_telegram_id_and_clear_bookings(
        session,
        telegram_id=query.from_user.id)
    await dialog_manager.switch_to(state=Desk.main_menu)