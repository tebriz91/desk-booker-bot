import re
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_room_by_name, orm_insert_room

class InputError(Exception):
    pass

async def room_add_service(session: AsyncSession, room_name: str) -> str:
    room_name = room_name.strip()
    if not room_name or " " in room_name:
        raise InputError("Please enter a valid input without spaces.\nFor example: 108 or A")
    
    # Validate room_name according to the requirements: 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores
    if not re.match(r'^[A-Za-zА-Яа-я0-9_]{1,10}$', room_name):
        raise InputError("Room name must be 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores. Please try again.")
    
    # Check if the room already exists
    existing_room = await orm_select_room_by_name(session, room_name)
    if existing_room:
        raise InputError("Room already exists.")
    
    await orm_insert_room(session, room_name)
    return f"Room with name: {room_name} has been added."