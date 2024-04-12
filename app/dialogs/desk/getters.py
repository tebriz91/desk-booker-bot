from typing import TYPE_CHECKING

from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from services.user.desk_assignment_checker import check_desk_assignment_by_telegram_id

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger
logger = Logger()


async def get_desk_assignment(dialog_manager: DialogManager,
                              i18n: TranslatorRunner,
                              event_from_user,
                              **kwargs):
    session: AsyncSession = dialog_manager.middleware_data['session']
    try:
        status, message = await check_desk_assignment_by_telegram_id(
        i18n,
        session,
        telegram_id=event_from_user.id)
    
        if status == "empty":
            return {'desk-assignment-empty': message}
        elif status == "active":
            return {'desk-assignment-active': message,
                    'button-toggle': i18n.button.toggle(),
                    'button-exit': i18n.button.exit()}
        elif status == "inactive":
            return {'desk-assignment-inactive': message,
                    'button-toggle': i18n.button.toggle(),
                    'button-exit': i18n.button.exit()}
        elif status == "error":
            return {'desk-assignment-error': message}
    
    except Exception as e:
        logger.info(f"Error in get_desk_assignment: {e}")
        return str(e)