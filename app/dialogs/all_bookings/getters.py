from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from services.common.rooms_list_generator import generate_available_rooms_as_list_of_tuples
from services.bookings_list_generator import AllBookingsError, generate_current_bookings_list_by_room_id


if TYPE_CHECKING:
    from locales.stub import TranslatorRunner


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
    session = dialog_manager.middleware_data['session']
    room_id = int(dialog_manager.dialog_data['room_id'])
    c = dialog_manager.start_data['bot_operation_config']
    
    try:
        status, response = await generate_current_bookings_list_by_room_id(
            i18n,
            session,
            date_format=c['date_format'],
            date_format_short=c['date_format_short'],
            room_id=room_id,
        )
        
        if status == "empty":
            return {'empty': response,
                    'button-back': i18n.button.back(),
                    'button-exit': i18n.button.exit()}

        elif status == "error":
            return {'error': response,
                    'button-back': i18n.button.back(),
                    'button-exit': i18n.button.exit()}
    
        elif status == "only-bookings":
            return {'bookings': response,
                    'button-back': i18n.button.back(),
                    'button-exit': i18n.button.exit()}
        
        elif status == "only-assignments":
            return {'bookings': response,
                    'button-back': i18n.button.back(),
                    'button-exit': i18n.button.exit()}
        
        elif status == "bookings-assignments":
            return {'bookings': response,
                    'button-back': i18n.button.back(),
                    'button-exit': i18n.button.exit()}
    
    except Exception as e:
        logger.info(f"Error in get_bookings: {e}")
        return str(e)