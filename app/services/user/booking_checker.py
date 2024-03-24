from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_booking_by_telegram_id_and_date_selectinload


async def check_existing_booking(session: AsyncSession, telegram_id: int, date: str, date_format: str) -> bool | str:
    """
    Checks if there is an existing booking for a given Telegram user ID on a specific date.

    Parameters:
    - session: AsyncSession - The SQLAlchemy async session for database operations.
    - telegram_id: int - The Telegram user ID.
    - date: str - The date in the format, defined in date_format in .env file.
    - date_format: str - The date format to display the dates with weekday.

    Returns:
    - bool | str: Boolean (False) if no booking exists or formatted string with existing booking info.
    """
    # Parse date string to datetime.date type: 'YYYY-MM-DD' to query the database. And handle incorrect date format.
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError as e:
        return f"Error: Incorrect date format. Parsing date to datetime.date failed."
    # Check if there is an existing booking for the given user ID and date.
    try:
        # To avoid lazy loading, use selectinload to load the related objects (room and desk) in one query.
        existing_booking = await orm_select_booking_by_telegram_id_and_date_selectinload(session, telegram_id, booking_date)
        
        if not existing_booking:
            return False
        else:
            return f"You already have a booking on {date} in room: {existing_booking.room.name} at desk: {existing_booking.desk.name}."
    except Exception as e:
        return "An unexpected error occurred while checking for existing bookings."