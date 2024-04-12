from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from services.common.rooms_list_generator import generate_available_rooms_as_list_of_tuples

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger

logger = Logger()


async def get_rooms(dialog_manager: DialogManager,
                    i18n: TranslatorRunner,
                    **kwargs):
    session = dialog_manager.middleware_data['session']
    rooms = await generate_available_rooms_as_list_of_tuples(session)
    if not rooms:
        return {'no-rooms': i18n.no.rooms(),
                'button-exit': i18n.button.exit()}
    else:
        return {'rooms': rooms,
                'select-room': i18n.select.room(),
                'button-exit': i18n.button.exit()}


async def get_bookings(dialog_manager: DialogManager,
                    i18n: TranslatorRunner,
                    **kwargs):
    bookings = dialog_manager.dialog_data['bookings']
    return {'bookings': bookings,
            'button-back': i18n.button.back(),
            'button-exit': i18n.button.exit()}