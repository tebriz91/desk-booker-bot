from typing import TYPE_CHECKING, Optional
from datetime import datetime, timedelta
import random

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_desk_id_by_name,
    orm_select_booking_by_desk_id_and_date,
    orm_insert_booking,
    orm_select_available_desks_by_date,
    orm_select_available_desks_by_desks_id_and_weekday,
    orm_select_team_preferred_room_id_by_telegram_id,
    DeskBookerError,
)
from database.enums.weekdays import Weekday

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

    
async def desk_booker_random(
    i18n,
    session: AsyncSession,
    telegram_id: int,
    date: str,
    date_format: str,
    advanced_mode: Optional[bool],
    standard_access_days: Optional[int] = 1,
) -> str:
    """
    Add a random booking to the database for any available desk on the given date.
    """
    i18n: TranslatorRunner = i18n
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError:
        return "Error: Incorrect date format. Parsing date to datetime.date failed."

    # Fetch all desks that are available and not booked on the specified date
    available_desks = await orm_select_available_desks_by_date(session, booking_date)
    if not available_desks:
        return "No available desks for the selected date."
    # Extract desk IDs for further filtering
    desk_ids = [desk.id for desk in available_desks]
    
    # Convert integer weekday to Weekday enum
    weekday_enum = Weekday(booking_date.weekday())

    # Fetch desks that are not assigned or where the assigned user is out of office
    desks_available_for_booking = await orm_select_available_desks_by_desks_id_and_weekday(session, desk_ids, weekday_enum)
    if not desks_available_for_booking:
        return "No desks are available due to assignments or office presence."
    
    try:
        # Non-advanced mode logic
        if not advanced_mode:
            # Select a random desk from the available ones
            desk = random.choice(desks_available_for_booking)
        
        # Advanced mode logic
        if advanced_mode:
            # Calculating workdays delta between today and booking date (excluding weekends)
            today = datetime.now().date()
            workdays_difference = 0
            while today <= booking_date:
                if today.weekday() < 5:  # Weekdays are from 0 (Monday) to 4 (Friday)
                    workdays_difference += 1
                today += timedelta(days=1)
            if workdays_difference <= standard_access_days:
                desk = random.choice(desks_available_for_booking)
            
            if workdays_difference > standard_access_days:
                # Retrieve preffered_room_id by telegram_id
                preferred_room_id = await orm_select_team_preferred_room_id_by_telegram_id(session, telegram_id)
                
                if not preferred_room_id:
                    #! desk-booker-random-no-desks
                    return i18n.desk.booker.random.no.desks(date=date)
                
                # Filter desks_available_for_booking by preferred_room_id
                filtered_desks = [desk for desk in desks_available_for_booking if desk.room_id == preferred_room_id]
                
                if not filtered_desks:
                    #! desk-booker-random-no-desks
                    return i18n.desk.booker.random.no.desks(date=date)
                
                else:
                    desk = random.choice(filtered_desks)
            
    except Exception as e:
        return f"Error {e}"
    
    # Attempt to create a booking
    try:
        await orm_insert_booking(session, telegram_id, desk.id, booking_date)
        #! desk-booker-success
        return i18n.desk.booker.success(date=date, room_name=desk.room.name, desk_name=desk.name)
    except Exception as e:
        return f"Error while attempting to create booking: {e}"