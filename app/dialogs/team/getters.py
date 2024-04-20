from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from services.user.team_info_getter import get_team_info_service


if TYPE_CHECKING:
    from locales.stub import TranslatorRunner


async def get_team_info(dialog_manager: DialogManager,
                    i18n: TranslatorRunner,
                    event_from_user,
                    **kwargs):
    session = dialog_manager.middleware_data['session']
    try:
        status, response = await get_team_info_service(i18n, session, telegram_id=event_from_user.id)
    
        if status == "empty":
            return {'empty': response,
                    'button-exit': i18n.button.exit()}

        elif status == "no-info":
            return {'no-info': response,
                    'button-exit': i18n.button.exit()}
        
        elif status == "team-info":
            return {'team-info': response,
                    'button-exit': i18n.button.exit()}
        
    except Exception as e:
        return str(e)