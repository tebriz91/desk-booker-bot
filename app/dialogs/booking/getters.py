from aiogram_dialog import DialogManager

from services.user.dates_generator import generate_dates
from services.common.rooms_list_generator import generate_available_rooms_list


async def get_dates(dialog_manager: DialogManager, **kwargs):
    config = dialog_manager.start_data['bot_operation_config']
    dates = await generate_dates(
        config['num_days'],
        config['exclude_weekends'],
        config['timezone'],
        config['country_code'],
        config['date_format'],
    )
    return {'dates': dates}


async def get_rooms(dialog_manager: DialogManager, **kwargs):
    # Get session from DataBaseSession middleware
    session = dialog_manager.middleware_data['session']
    rooms = await generate_available_rooms_list(session)
    return {'rooms': rooms}


async def get_desks(dialog_manager: DialogManager, **kwargs):
    desks: list = dialog_manager.dialog_data['desks']
    return {'desks': desks}