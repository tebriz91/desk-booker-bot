from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_bookings_by_telegram_id_joined_from_today

async def generate_html_formatted_string_with_users_bookings(
    session: AsyncSession,
    date_format: str,
    date_format_short: str,
    telegram_id: int,
    telegram_name: str | None = "Anonymous user"
    ) -> str:
    """
    Generates a formatted string with the list of bookings.
# 
    Args:
    - session (AsyncSession): SQLAlchemy AsyncSession
    - telegram_id (int): Telegram user id
    
    Returns:
    - bookings_fstring (str): Formatted string with the list of bookings
    """
    bookings_fstring: str = ""
    # Extract bookings from the database
    bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
    
    first_line = f"Your bookings, @{telegram_name}:\n\n"

    for booking in bookings_obj:
        formatted_booking = (
            f"<b>{booking.date.strftime(date_format)}</b>\n"
            f"Room: {booking.room.name}, Desk: {booking.desk.name}\n"
            f"<pre>booked on: {booking.created_at.strftime(date_format_short)}</pre>\n\n"
        )
        bookings_fstring += formatted_booking

    bookings_fstring = first_line + bookings_fstring

    return bookings_fstring