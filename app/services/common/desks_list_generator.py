from typing import List, Optional, Union
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_available_desks_by_room_name,
    orm_select_room_id_by_name,
    orm_select_available_desks_by_desks_id_and_weekday,
    orm_select_team_id_by_telegram_id,
    orm_select_team_preferred_room_id,
    orm_select_available_not_booked_desks_by_room_id,
)
from database.enums.weekdays import Weekday


async def generate_available_desks_list(session: AsyncSession, room_name: str) -> List[str]:
    desks_orm_obj = await orm_select_available_desks_by_room_name(session, room_name)
    return [desk.name for desk in desks_orm_obj]


async def parse_booking_date(date: str, date_format: str) -> Union[datetime.date, str]:
    try:
        return datetime.strptime(date, date_format).date()
    except ValueError:
        return "Error: Incorrect date format. Parsing date to datetime.date failed."


async def fetch_desks_list(
    session: AsyncSession,
    room_id: int,
    weekday: Weekday,
    booking_date: datetime.date,
    ) -> List: # Alternative 
    try:
        not_booked_desks_obj = await orm_select_available_not_booked_desks_by_room_id(session, room_id, booking_date)
        not_booked_desks_id = [desk.id for desk in not_booked_desks_obj]
        # Get the desks that are not assigned and not booked by
        desks_obj = await orm_select_available_desks_by_desks_id_and_weekday(session, not_booked_desks_id, weekday)
        for desk in desks_obj:
            desks = [desk.name for desk in desks_obj]
        return desks if desks else []
    except Exception as e:
        raise RuntimeError(f"Error retrieving desks: {e}")


async def generate_desks_list(
    session: AsyncSession,
    room_name: str,
    date: str,
    date_format: str,
    advanced_mode: Optional[bool],
    telegram_id: Optional[int],
    standard_access_days: Optional[int] = 1,
    ) -> Union[List[str], str]:
    booking_date = await parse_booking_date(date, date_format)
    if isinstance(booking_date, str):
        return booking_date  # Return error message if parsing failed
    
    # Convert integer weekday to Weekday enum
    weekday_enum = Weekday(booking_date.weekday())
    today = datetime.now().date()

    # Calculating workdays delta between today and booking date (excluding weekends)
    workdays_difference = 0
    current_day = today
    while current_day <= booking_date:
        if current_day.weekday() < 5:  # Weekdays are from 0 (Monday) to 4 (Friday)
            workdays_difference += 1
        current_day += timedelta(days=1)
    
    # Fetch the room ID based on room name
    room_id = await orm_select_room_id_by_name(session, room_name)
    if not room_id:
        return f"Error: Room '{room_name}' not found"

    # Advanced mode logic
    try:
        if advanced_mode:
            team_id = await orm_select_team_id_by_telegram_id(session, telegram_id)
            preferred_room_id = await orm_select_team_preferred_room_id(session, team_id) if team_id else None
            # User can book if (one of the following conditions is met):
            # - No team_id or preferred_room_id != room_id but within standard access days
            # - Preferred room matches selected room despite workdays_difference
            if preferred_room_id != room_id and workdays_difference > standard_access_days:
                return []
            elif not team_id and workdays_difference > standard_access_days:
                return []
            elif not team_id or preferred_room_id == room_id or workdays_difference <= standard_access_days:
                desks = await fetch_desks_list(session, room_id, weekday_enum, booking_date)
                return desks if desks else []
            else:
                raise RuntimeError("Error: Unknown advanced mode logic")
    except Exception as e:
        raise RuntimeError(f"Error in advanced mode logic: {e}")
    
    # Non-advanced mode logic
    try:
        if not advanced_mode:
            desks = await fetch_desks_list(session, room_id, weekday_enum, booking_date)
            return desks if desks else []
    except Exception as e:
        raise RuntimeError(f"Error in non-advanced mode logic: {e}")