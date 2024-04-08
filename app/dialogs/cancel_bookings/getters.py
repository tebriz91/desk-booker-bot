from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from services.bookings_list_generator import generate_current_bookings_by_telegram_id

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger

logger = Logger()


async def get_bookings(dialog_manager: DialogManager, i18n: TranslatorRunner, event_from_user, **kwargs):
    # Get session from DataBaseSession middleware
    session: AsyncSession = dialog_manager.middleware_data['session']
    # Get the bot operation configuration
    config = dialog_manager.start_data['bot_operation_config']
    # Get the current bookings for the user as a list of tuples, where the first element is the booking ID, and the second is the booking data
    bookings = await generate_current_bookings_by_telegram_id(
        i18n,
        session,
        date_format=config['date_format'],
        telegram_id=event_from_user.id,
    )
    # Base response structure
    response_data = {
        'select-booking-to-cancel': i18n.select.booking.to.cancel(),
        'bookings-to-cancel': [],  # Initialize with an empty list to ensure structure
        'button-exit': i18n.button.exit(),
    }    
    try:
        if isinstance(bookings, str):
            # Log and return the error while maintaining structure
            logger.info(f"Inside getter. Error: {bookings}")
            response_data['cancel-booking-error'] = bookings
        elif not bookings:
            # No bookings case
            logger.info("No bookings found")
            response_data['no-bookings-to-cancel'] = i18n.no.bookings.to.cancel()
        else:
            # Bookings exist, update the list
            logger.info(f"Inside getter. Bookings List: {bookings}")
            response_data['bookings-to-cancel'] = bookings
    except Exception as e:
        logger.info(f"Error in get_bookings: {e}")
        response_data['cancel-booking-error'] = str(e)
    
    return response_data