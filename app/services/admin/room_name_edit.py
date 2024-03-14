import re
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_room_by_name, orm_update_room_name_by_name

class InputError(Exception):
    pass

async def room_name_edit_service(
    session: AsyncSession,
    old_room_name: str,
    new_room_name: str | None
    ) -> str:
    new_room_name = new_room_name.strip()
    if not new_room_name or " " in new_room_name:
        raise InputError("Please enter a valid input without spaces.\nFor example: 108 or A")
    
    if old_room_name == new_room_name:
        raise InputError("New room name must be different from the old one.")
    
    # Validate room_name according to the requirements: 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores
    if not re.match(r'^[A-Za-zА-Яа-я0-9_]{1,10}$', new_room_name):
        raise InputError("Room name must be 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores. Please try again.")
    
    # Check if the room with the new name already exists
    existing_room = await orm_select_room_by_name(session, new_room_name)
    if existing_room:
        raise InputError(f"Room with name: '{new_room_name}' already exists.")
    
    try:
        await orm_update_room_name_by_name(session, old_room_name, new_room_name)
        return f"Room with name: {old_room_name} has been renamed to: {new_room_name}."
    except Exception as e:
        raise e