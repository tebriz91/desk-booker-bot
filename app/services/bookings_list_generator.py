from typing import Dict, List, TYPE_CHECKING, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Booking, DeskAssignment

from database.orm_queries import (
    orm_select_bookings_by_room_id_joined_from_today, orm_select_bookings_by_telegram_id_joined_from_today,orm_select_desk_assignments_by_room_id_selectinload,
    orm_select_team_name_by_id,
    orm_select_bookings_by_team_id_joined_from_today,
    orm_select_desk_assignments_by_team_id_selectinload,
)

if TYPE_CHECKING:
    from locales.stub import TranslatorRunner


class AllBookingsError(Exception):
    pass


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
    ) -> Tuple[str, str]:
    '''
    Returns a tuple of two strings: the first string a tag for the response, and the second string is the response message.
    '''
    i18n: TranslatorRunner = i18n
    # Fetch bookings for the given room from the database
    bookings = await orm_select_bookings_by_room_id_joined_from_today(session, room_id)
    assignments = await orm_select_desk_assignments_by_room_id_selectinload(session, room_id)
    
    if bookings:
        # Get room_name
        room_name = bookings[0].desk.room.name
        room_plan = bookings[0].desk.room.plan
        # Initialize a dictionary to store bookings organized by date
        bookings_by_date: Dict[str, List[Booking]] = {}

        # Iterate over each booking
        for booking in bookings:
            # Format the booking date as per the given date format
            booking_date = booking.date.strftime(date_format)

            # If this date is not already a key in the dictionary, add it
            if booking_date not in bookings_by_date:
                bookings_by_date[booking_date] = []

            # Append the current booking to the list of bookings for this date
            bookings_by_date[booking_date].append(booking)

        # Initialize an empty string to accumulate the formatted booking information
        list_of_bookings: str = ''

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
        
        response_bookings: str = first_line + list_of_bookings
    
    if assignments:
        # Get room_name
        room_name = assignments[0].desk.room.name
        
        # Desk assignments by weekday
        assignments_by_weekday: Dict[str, List[DeskAssignment]] = {}
        
        # Iterate over each assignment
        for assignment in assignments:
            # Format the weekday
            weekday = assignment.weekday.name
            # If this weekday is not already a key in the dictionary, add it
            if weekday not in assignments_by_weekday:
                assignments_by_weekday[weekday] = []
            # Append the current assignment to the list of assignments for this weekday
            assignments_by_weekday[weekday].append(assignment)
        
        list_of_assignments: str = ''
        
        # Iterate over each weekday and its associated assignments
        for weekday, assignments in assignments_by_weekday.items():
            # Add the weekday as a header
            #! all-bookings-desk-assignments-weekday
            list_of_assignments += i18n.all.bookings.desk.assignments.weekday(weekday=weekday) + '\n'
            # Add each assignment under this weekday
            for assignment in assignments:
                #! all-bookings-desk-user
                list_of_assignments += i18n.all.bookings.desk.user(
                    desk_name=assignment.desk.name,
                    telegram_name=f'@{assignment.user.telegram_name}'
                ) + '\n'
            # Add a newline for separation between different weekdays
            list_of_assignments += '\n'
        # The first line of the final output
        #! all-bookings-desk-assignments-first-line
        first_line = i18n.all.bookings.desk.assignments.first.line(room_name=room_name) + '\n\n'

        response_assignments = first_line + list_of_assignments

    if bookings and assignments:
        final_response = response_bookings + response_assignments
        return ("bookings-assignments", final_response)
    
    if bookings and not assignments:
        return ("only-bookings", response_bookings)
    
    if not bookings and assignments:
        #! all-bookings-no-bookings
        final_response = i18n.all.bookings.no.bookings() + '\n\n' + response_assignments
        return ("only-assignments", final_response)
    
    if not bookings and not assignments:
        #! all-bookings-no-bookings-assignments
        return ("empty", i18n.all.bookings.no.bookings.assignments())
    
    return ("error", "An unexpected error occurred while generating the bookings list.")


async def generate_current_bookings_list_by_team_id(
    i18n,
    session: AsyncSession,
    date_format: str,
    date_format_short: str,
    team_id: int
    ) -> Tuple[str, str]:
    '''
    Returns a tuple of two strings: the first string a tag for the response, and the second string is the response message.
    '''
    i18n: TranslatorRunner = i18n
    # Get team_name
    team_name = await orm_select_team_name_by_id(session, team_id)
    # Fetch bookings for the given team from the database
    bookings = await orm_select_bookings_by_team_id_joined_from_today(session, team_id)
    assignments = await orm_select_desk_assignments_by_team_id_selectinload(session, team_id)
    
    if not bookings and not assignments:
        # Handle the case where both lists are empty
        #! team-bookings-no-bookings-assignments
        return ("empty", i18n.team.bookings.no.bookings.assignments(team_name=team_name))
    
    if bookings:
        # Initialize a dictionary to store bookings organized by date
        bookings_by_date: Dict[str, List[Booking]] = {}

        # Iterate over each booking
        for booking in bookings:
            # Format the booking date as per the given date format
            booking_date = booking.date.strftime(date_format)
    
            # If this date is not already a key in the dictionary, add it
            if booking_date not in bookings_by_date:
                bookings_by_date[booking_date] = []

            # Append the current booking to the list of bookings for this date
            bookings_by_date[booking_date].append(booking)

        # Initialize an empty string to accumulate the formatted booking information
        list_of_bookings: str = ''

        # Iterate over each date and its associated bookings
        for date, bookings in bookings_by_date.items():
            # Add the date as a header
            #! team-bookings-date
            list_of_bookings += i18n.team.bookings.date(date=date) + '\n'
            # Add each booking under this date
            for booking in bookings:
                #! team-bookings-room-desk-user
                list_of_bookings += i18n.team.bookings.room.desk.user(room_name=booking.desk.room.name, desk_name=booking.desk.name, telegram_name=f'@{booking.user.telegram_name}') + '\n'
            # Add a newline for separation between different dates
            list_of_bookings += '\n'
        # The first line of the final output
        #! team-bookings-first-line
        first_line = i18n.team.bookings.first.line(team_name=team_name) + '\n\n'
        
        response_bookings: str = first_line + list_of_bookings
    
    if assignments:
        # Desk assignments by weekday
        assignments_by_weekday: Dict[str, List[DeskAssignment]] = {}
        
        # Iterate over each assignment
        for assignment in assignments:
            # Format the weekday
            weekday = assignment.weekday.name
            # If this weekday is not already a key in the dictionary, add it
            if weekday not in assignments_by_weekday:
                assignments_by_weekday[weekday] = []
            # Append the current assignment to the list of assignments for this weekday
            assignments_by_weekday[weekday].append(assignment)
        
        list_of_assignments: str = ''
        
        # Iterate over each weekday and its associated assignments
        for weekday, assignments in assignments_by_weekday.items():
            # Add the weekday as a header
            #! team-bookings-desk-assignments-weekday
            list_of_assignments += i18n.team.bookings.desk.assignments.weekday(weekday=weekday) + '\n'
            # Add each assignment under this weekday
            for assignment in assignments:
                #! team-bookings-room-desk-user
                list_of_assignments += i18n.team.bookings.room.desk.user(
                    room_name=assignment.desk.room.name,
                    desk_name=assignment.desk.name,
                    telegram_name=f'@{assignment.user.telegram_name}'
                ) + '\n'
            # Add a newline for separation between different weekdays
            list_of_assignments += '\n'
        # The first line of the final output
        #! team-bookings-desk-assignments-first-line
        first_line = i18n.team.bookings.desk.assignments.first.line(team_name=team_name) + '\n\n'

        response_assignments = first_line + list_of_assignments

    if bookings and assignments:
        final_response = response_bookings + response_assignments
        return ("bookings-assignments", final_response)
    
    if bookings and not assignments:
        return ("only-bookings", response_bookings)
    
    if not bookings and assignments:
        #! team-bookings-no-bookings-message
        final_response = i18n.team.bookings.no.bookings.message(team_name=team_name) + '\n\n' + response_assignments
        return ("only-assignments", final_response)

    return ("error", "An unexpected error occurred while generating the bookings list.")


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
    bookings_obj = await orm_select_bookings_by_telegram_id_joined_from_today(session, telegram_id)
    try:
        if not bookings_obj:
            return []
        else:
            for booking in bookings_obj:
                date = booking.date.strftime(date_format)
                room_name = booking.desk.room.name
                desk_name = booking.desk.name
                booking_data = i18n.bookings.to.cancel(date=date, room_name=room_name, desk_name=desk_name)
                bookings_list.append((booking.id, booking_data))
            return bookings_list
    except Exception as e:
        return f"Error: {e}"