from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from services.user.team_info_getter import get_team_info_service
from services.bookings_list_generator import generate_current_bookings_list_by_team_id


if TYPE_CHECKING:
    from locales.stub import TranslatorRunner


async def get_team_info(dialog_manager: DialogManager,
                    i18n: TranslatorRunner,
                    event_from_user,
                    **kwargs):
    session = dialog_manager.middleware_data['session']
    try:
        response = await get_team_info_service(i18n, session, telegram_id=event_from_user.id)
        
        if len(response) == 2:
            status, message = response
            team_id = None
        else:
            status, message, team_id = response
            
        if status == "empty":
            return {'empty': message,
                    'button-exit': i18n.button.exit()}

        elif status == "no-info":
            return {'no-info': message,
                    'button-exit': i18n.button.exit()}
        
        elif status == "team-info":
            dialog_manager.dialog_data['team_id'] = team_id
            return {'team-info': message,
                    'team-button-bookings': i18n.team.button.bookings(),
                    'button-exit': i18n.button.exit()}
        
    except Exception as e:
        return str(e)


async def get_team_bookings(dialog_manager: DialogManager,
                            i18n: TranslatorRunner,
                            **kwargs):
    session = dialog_manager.middleware_data['session']
    team_id = int(dialog_manager.dialog_data['team_id'])
    c = dialog_manager.start_data['bot_operation_config']

    try:
        status, response = await generate_current_bookings_list_by_team_id(
            i18n,
            session,
            date_format=c['date_format'],
            date_format_short=c['date_format_short'],
            team_id=team_id,
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
        return str(e)