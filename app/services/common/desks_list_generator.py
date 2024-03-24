from typing import List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_available_desks_by_room_name,
    orm_select_room_id_by_name,
    orm_select_available_not_booked_desks_by_room_id)


async def generate_available_desks_list(session: AsyncSession, room_name: str) -> List[str]:
    desks_orm_obj = await orm_select_available_desks_by_room_name(session, room_name)
    return [desk.name for desk in desks_orm_obj]

async def generate_available_not_booked_desks_list(
    session: AsyncSession,
    room_name: str,
    date: str,
    date_format: str,
    ) -> List[str] | str:
    room_id = await orm_select_room_id_by_name(session, room_name)
    
    try:
        booking_date = datetime.strptime(date, date_format).date()
    except ValueError:
        return f"Error: Incorrect date format. Parsing date to datetime.date failed."
    
    try:
        desk_orm_obj = await orm_select_available_not_booked_desks_by_room_id(session, room_id, booking_date)
        return [desk.name for desk in desk_orm_obj]
    except Exception as e:
        return f"Error: {e}"