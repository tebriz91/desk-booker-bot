from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_bookings_by_telegram_id_joined_from_today

# Generate a formatted string (with HTML tags) with the list of bookings
async def generate_list_of_current_bookings_by_telegram_id(
    session: AsyncSession,
    date_format: str,
    date_format_short: str,
    telegram_id: int,
    telegram_name: str | None = "Anonymous user"
    ) -> str:
    """
    Args:
    - session (AsyncSession): SQLAlchemy AsyncSession
    - date_format (str): Date format with weekday
    - date_format_short (str): Date format without weekday
    - telegram_id (int): Telegram user id
    - telegram_name (str): Telegram user name
    
    Returns:
    - bookings (str): Formatted string with the list of bookings
    """
    first_line = f"Your bookings, @{telegram_name}:\n\n"
    list_of_bookings: str = ""
    bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
    try:
        if not bookings_obj:
            return f"You have no bookings yet"
        else:
            for booking in bookings_obj:
                formatted_booking = (
                    f"<b>{booking.date.strftime(date_format)}</b>\n"
                    f"Room: {booking.room.name}, Desk: {booking.desk.name}\n"
                    f"<pre>booked on: {booking.created_at.strftime(date_format_short)}</pre>\n\n"
                )
                list_of_bookings += formatted_booking
            bookings = first_line + list_of_bookings
            return bookings
    except Exception as e:
        return f"Error: {e}"

async def generate_list_of_all_current_bookings(
    session: AsyncSession,
    date_format: str,
    date_format_short: str
    ) -> str:
    first_line = "Current bookings:\n\n"
    list_of_bookings: str = ""
    bookings_obj = await orm_select_all_bookings_joined_from_today(session)
    try:
        if not bookings_obj:
            return f"No bookings yet"
        else:
            for booking in bookings_obj:
                formatted_booking = (
                    f"<b>{booking.date.strftime(date_format)}</b>\n"
                    f"Room: {booking.room.name}, Desk: {booking.desk.name}\n"
                    f"User: @{booking.telegram_name}\n"
                    f"<pre>booked on: {booking.created_at.strftime(date_format_short)}</pre>\n\n"
                )
                list_of_bookings += formatted_booking
            bookings = first_line + list_of_bookings
            return bookings
    except Exception as e:
        return f"Error: {e}"