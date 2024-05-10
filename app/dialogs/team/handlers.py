from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Select
from aiogram.types import CallbackQuery

from app.states.states import Team


async def selected_team_bookings(query: CallbackQuery,
                                 widget: Select,
                                 dialog_manager: DialogManager,
                                 ) -> None:
    
    await dialog_manager.switch_to(Team.view_bookings)