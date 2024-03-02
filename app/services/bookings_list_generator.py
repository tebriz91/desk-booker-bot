from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Booking

from database.orm_queries import orm_select_bookings_by_room_id_joined_from_today, orm_select_bookings_by_telegram_id_joined_from_today

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
                    f"<code>booked on: {booking.created_at.strftime(date_format_short)}</code>\n\n"
                )
                list_of_bookings += formatted_booking
            return first_line + list_of_bookings
    except Exception as e:
        return f"Error: {e}"

async def generate_list_of_all_current_bookings_by_room_id(
    session: AsyncSession,
    date_format: str,
    date_format_short: str,
    room_id: int
) -> str:
    """
    Generate a formatted string of all current bookings by room ID, organized by dates.

    Args:
    - session (AsyncSession): SQLAlchemy AsyncSession for database operations.
    - date_format (str): Date format to display the dates with weekday.
    - date_format_short (str): Short date format.
    - room_id (int): ID of the room for which bookings are to be fetched.

    Returns:
    - bookings (str): Formatted string with the list of bookings organized by dates.
    """
    try:
        # Fetch bookings for the given room from the database
        bookings_obj = await orm_select_bookings_by_room_id_joined_from_today(session, room_id)
        
        # If there are no bookings, return a message stating so
        if not bookings_obj:
            return f"There are no bookings in this room yet"

        # Initialize a dictionary to store bookings organized by date
        bookings_by_date: Dict[str, List[Booking]] = {}

        # Iterate over each booking
        for booking in bookings_obj:
            # Format the booking date as per the given date format
            booking_date = booking.date.strftime(date_format)

            # If this date is not already a key in the dictionary, add it
            if booking_date not in bookings_by_date:
                bookings_by_date[booking_date] = []

            # Append the current booking to the list of bookings for this date
            bookings_by_date[booking_date].append(booking)

        # Initialize an empty string to accumulate the formatted booking information
        list_of_bookings = ""

        # Iterate over each date and its associated bookings
        for date, bookings in bookings_by_date.items():
            # Add the date as a header
            list_of_bookings += f"<b>{date}</b>\n"
            # Add each booking under this date
            for booking in bookings:
                list_of_bookings += f"Desk: {booking.desk.name}, @{booking.user.telegram_name}\n"
            # Add a newline for separation between different dates
            list_of_bookings += "\n"

        # The first line of the final output
        first_line = f"All bookings in Room: {booking.room.name}\n\n"

        # Return the complete formatted bookings string
        return first_line + list_of_bookings

    except Exception as e:
        # In case of any error, return an error message
        return f"Error: {e}"
    
# Generate a dict of current bookings by telegram ID to be used in InlineKeyboardBuilder to create a list of buttons
async def generate_dict_of_current_bookings_by_telegram_id_for_inline_kb(
    session: AsyncSession,
    date_format: str,
    telegram_id: int
    ) -> Dict[Booking.id, str]:
    """
    Args:
    - session (AsyncSession): SQLAlchemy AsyncSession
    - telegram_id (int): Telegram user id
    - date_format (str): Date format with weekday
    
    Returns:
    - bookings (Dict[int, str]): Dict with booking ID as key and formatted string with the booking info (desk name, room name, booking date) as value
    """
    
    bookings: Dict[Booking.id: int, str] = {}
    
    bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
    
    # If there are no bookings, return an empty dict
    if not bookings_obj:
        return {}
    # If there are bookings, return a dict with booking ID as key and formatted string with the booking info (desk name, room name, booking date) as value
    else:
        for booking in bookings_obj:
            formatted_booking = (
                f"Desk {booking.desk.name} (room {booking.room.name}) on {booking.date.strftime(date_format)}"
            )
            # Add the formatted booking to the dict
            bookings[booking.id] = formatted_booking
        return bookings