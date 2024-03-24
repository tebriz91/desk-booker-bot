from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_room_id_by_name,
    orm_select_desk_id_by_name,
    orm_select_booking_by_desk_id_and_date,
    orm_insert_booking,
    DeskBookerError,
)


async def desk_booker(
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
    room_id = await orm_select_room_id_by_name(session, room_name)
    desk_id = await orm_select_desk_id_by_name(session, desk_name)
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError as e:
        return f"Error: Incorrect date format. Parsing date to datetime.date failed."
    
    # Check for an existing booking for the same desk and date
    existing_booking = await orm_select_booking_by_desk_id_and_date(session, desk_id, booking_date)
    
    if existing_booking:
        return "Oops... Someone has booked the desk before you. Please select another desk."
    
    try:
        await orm_insert_booking(session, telegram_id, desk_id, room_id, booking_date)
        return f"Your booking for <b>{date}</b> in room: <b>{room_name}</b> at desk: <b>{desk_name}</b> has been successfully made."
    except Exception as e:
        return f"Error: {e}"