from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from services.user.dates_generator import generate_dates
from services.common.rooms_list_generator import generate_available_rooms_list

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger
logger = Logger()


async def get_dates(dialog_manager: DialogManager, i18n: TranslatorRunner, **kwargs):
    config = dialog_manager.start_data['bot_operation_config']
    dates = await generate_dates(
        config['num_days'],
        config['exclude_weekends'],
        config['timezone'],
        config['country_code'],
        config['date_format'],
    )
    return {'dates': dates,
            'select-date': i18n.select.date(),
            'button-exit': i18n.button.exit()}


async def get_rooms(dialog_manager: DialogManager,
                    i18n: TranslatorRunner,
                    **kwargs):
    # Get session from DataBaseSession middleware
    session = dialog_manager.middleware_data['session']
    # TODO: Refactor to get list of tuples with room_id and room_name
    rooms = await generate_available_rooms_list(session)
    if not rooms:
        return {'no-rooms': i18n.no.rooms(),
                'button-back': i18n.button.back(),
                'button-exit': i18n.button.exit()}
    else:
        date = dialog_manager.dialog_data['date']
        return {'rooms': rooms,
                'selected-date': i18n.selected.date(date=date),
                'select-room': i18n.select.room(),
                'button-back': i18n.button.back(),
                'button-exit': i18n.button.exit()}


async def get_desks(dialog_manager: DialogManager,
                    i18n: TranslatorRunner,
                    **kwargs):
    desks: list = dialog_manager.dialog_data['desks']
    date = dialog_manager.dialog_data['date']
    room_name = dialog_manager.dialog_data['room_name']
    room_plan = dialog_manager.dialog_data['room_plan_url']
    return {'desks': desks,
            'room_plan': room_plan,
            'selected-date': i18n.selected.date(date=date),
            'selected-room': i18n.selected.room(room_name=room_name),
            'select-desk': i18n.select.desk(),
            'button-back': i18n.button.back(),
            'button-exit': i18n.button.exit()}
