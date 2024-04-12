from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_room_id_by_name,
    orm_select_desk_id_by_name,
    orm_select_booking_by_desk_id_and_date,
    orm_insert_booking,
    DeskBookerError,
)

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner


async def desk_booker(
    i18n,
    session: AsyncSession,
    telegram_id: int,
    desk_name: str,
    room_name: str,
    date: str,
    date_format: str,
    ) -> str:
    """
    Add a booking to the database.
    
    Args:
    - session (AsyncSession): SQLAlchemy AsyncSession
    - telegram_id (int): Telegram user ID
    - desk_name (str): Desk name
    - room_name (str): Room name
    - date (str): Date in the format defined in the .env file
    - date_format (str): Date format to display the dates with weekday
    
    Returns:
    - str: Response message
    """
    i18n: TranslatorRunner = i18n
    desk_id = await orm_select_desk_id_by_name(session, desk_name)
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError as e:
        return "Error: Incorrect date format. Parsing date to datetime.date failed."
    
    # Check for an existing booking for the same desk and date
    existing_booking = await orm_select_booking_by_desk_id_and_date(session, desk_id, booking_date)
    
    if existing_booking:
        #! desk-booker-error
        raise DeskBookerError(i18n.desk.booker.error())
    
    try:
        await orm_insert_booking(session, telegram_id, desk_id, booking_date)
        #! desk-booker-success
        return i18n.desk.booker.success(date=date, room_name=room_name, desk_name=desk_name)
    except Exception as e:
        return f"Error: {e}"