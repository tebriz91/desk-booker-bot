from typing import Dict, List, TYPE_CHECKING, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Booking

from database.orm_queries import orm_select_bookings_by_room_id_joined_from_today, orm_select_bookings_by_telegram_id_joined_from_today

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner

from utils.logger import Logger

logger = Logger()


class AllBookingsError(Exception):
    pass


# async def generate_list_of_current_bookings_by_telegram_id(
#     i18n,
#     session: AsyncSession,
#     date_format: str,
#     date_format_short: str,
#     telegram_id: int,
#     telegram_name: str | None = "Anonymous user"
# ) -> str:
#     i18n: TranslatorRunner = i18n
#     bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
#     try:
#         if not bookings_obj:
#             #! my-bookings-no-bookings
#             return i18n.my.bookings.no.bookings()
#         else:
#             #! my-bookings-greeting
#             list_of_bookings: str = i18n.my.bookings.greeting(telegram_name=f'@{telegram_name}') + "\n\n"
#             for booking in bookings_obj:
#                 #! my-bookings-date
#                 date = i18n.my.bookings.date(date=booking.date.strftime(date_format))
#                 #! my-bookings-desk
#                 desk = i18n.my.bookings.desk(room_name=booking.room.name, desk_name=booking.desk.name)
#                 #! my-bookings-bookedOn
#                 booked_on = i18n.my.bookings.bookedOn(booked_on=booking.created_at.strftime(date_format_short))
#                 list_of_bookings += f"{date}\n{desk}\n{booked_on}\n\n"
#             return list_of_bookings
#     except Exception as e:
#         return f"Error: {e}"


async def generate_list_of_current_bookings_by_telegram_id(
    i18n,
    session: AsyncSession,
    date_format: str,
    date_format_short: str,
    telegram_id: int,
    telegram_name: str | None = "Anonymous user"
) -> str:
    i18n: TranslatorRunner = i18n
    bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
    try:
        if not bookings_obj:
            #! my-bookings-no-bookings
            return i18n.my.bookings.no.bookings()
        else:
            #! my-bookings-greeting
            list_of_bookings: str = i18n.my.bookings.greeting(telegram_name=f'@{telegram_name}') + '\n\n'
            for booking in bookings_obj:
                date = booking.date.strftime(date_format)
                room_name = booking.desk.room.name
                desk_name = booking.desk.name
                booked_on = booking.created_at.strftime(date_format_short)
                #! my-bookings-list
                list_of_bookings += i18n.my.bookings.list(date=date, room_name=room_name, desk_name=desk_name, booked_on=booked_on) + '\n\n'
            return list_of_bookings
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
        first_line = f"All bookings in Room: {booking.desk.room.name}\n\n"

        # Return the complete formatted bookings string
        return first_line + list_of_bookings

    except Exception as e:
        # In case of any error, return an error message
        return f"Error: {e}"


async def generate_current_bookings_list_by_room_id(
    i18n,
    session: AsyncSession,
    date_format: str,
    date_format_short: str,
    room_id: int
) -> str:
    i18n: TranslatorRunner = i18n
    logger.info('Inside generate_current_bookings_list_by_room_id')
    # Fetch bookings for the given room from the database
    bookings_obj = await orm_select_bookings_by_room_id_joined_from_today(session, room_id)
    
    # If there are no bookings, return a message stating so
    if not bookings_obj:
        #! all-bookings-no-bookings
        raise AllBookingsError(i18n.all.bookings.no.bookings())
    # Get room_name
    room_name = bookings_obj[0].desk.room.name
    room_plan = bookings_obj[0].desk.room.plan
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
    list_of_bookings = ''

    # Iterate over each date and its associated bookings
    for date, bookings in bookings_by_date.items():
        # Add the date as a header
        #! all-bookings-date
        list_of_bookings += i18n.all.bookings.date(date=date) + '\n'
        # Add each booking under this date
        for booking in bookings:
            #! all-bookings-desk-user
            list_of_bookings += i18n.all.bookings.desk.user(desk_name=booking.desk.name, telegram_name=f'@{booking.user.telegram_name}') + '\n'
        # Add a newline for separation between different dates
        list_of_bookings += '\n'
    # The first line of the final output
    #! all-bookings-greeting
    first_line = i18n.all.bookings.greeting(room_name=room_name) + '\n\n'
    # Return the complete formatted bookings string
    return first_line + list_of_bookings


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


async def generate_current_bookings_by_telegram_id(
    i18n,
    session: AsyncSession,
    date_format: str,
    telegram_id: int
) -> Union[List[Tuple[int, str]], str]:
    """
    Args:
    - i18n (TranslatorRunner): TranslatorRunner instance
    - session (AsyncSession): SQLAlchemy AsyncSession
    - telegram_id (int): Telegram user id
    - date_format (str): Date format with weekday
    
    Returns:
    - If successful, returns a list of tuples where each tuple contains booking_id (int)
      and a string with the booking data: date, room_name, desk_name.
    - If an error occurs, returns a string describing the error.
    """
    i18n: TranslatorRunner = i18n
    bookings_list: List[Tuple[int, str]] = []
    logger.info(f"Generating current bookings by telegram ID: {telegram_id}")
    bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
    try:
        if not bookings_obj:
            logger.info("No bookings found")
            return []
        else:
            for booking in bookings_obj:
                date = booking.date.strftime(date_format)
                room_name = booking.desk.room.name
                desk_name = booking.desk.name
                booking_data = i18n.bookings.to.cancel(date=date, room_name=room_name, desk_name=desk_name)
                bookings_list.append((booking.id, booking_data))
            logger.info(f"Result of generate_current_bookings_by_telegram_id: {bookings_list}")
            return bookings_list
    except Exception as e:
        logger.info(f"Error: {e}")
        return f"Error: {e}"