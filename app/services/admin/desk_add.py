import re
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import orm_select_desk_by_name, orm_select_room_id_by_name, orm_insert_desk_with_room_id


class InputError(Exception):
    pass


async def desk_add_service(session: AsyncSession, room_name: str, desk_name: str) -> str:
    desk_name = desk_name.strip()
    if not desk_name or " " in desk_name:
        raise InputError("Please enter a valid input without spaces.\nFor example: 23450 or A1")
    
    # Validate desk_name according to the requirements: 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores
    if not re.match(r'^[A-Za-zА-Яа-я0-9_]{1,10}$', desk_name):
        raise InputError("Desk name must be 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores. Please try again.")
    
    # Check if the desk already exists
    existing_desk = await orm_select_desk_by_name(session, desk_name)
    if existing_desk:
        raise InputError(f"Desk with the name: {desk_name} already exists.")
    
    # Retrieve room_id by room_name
    room_id = await orm_select_room_id_by_name(session, room_name)
    
    await orm_insert_desk_with_room_id(session, room_id, desk_name)
    return f"Desk with name: {desk_name} has been added."