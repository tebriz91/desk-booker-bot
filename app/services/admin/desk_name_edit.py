import re
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import orm_select_desk_by_name, orm_update_desk_name_by_name


class InputError(Exception):
    pass


async def desk_name_edit_service(
    session: AsyncSession,
    room_name: str,
    old_desk_name: str,
    new_desk_name: str | None
    ) -> str:
    new_desk_name = new_desk_name.strip()
    if not new_desk_name or " " in new_desk_name:
        raise InputError("Please enter a valid input without spaces.\nFor example: 23450 or A1")
    
    if old_desk_name == new_desk_name:
        raise InputError("New desk name must be different from the old one.")
    
    # Validate desk_name according to the requirements: 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores
    if not re.match(r'^[A-Za-zА-Яа-я0-9_]{1,10}$', new_desk_name):
        raise InputError("Desk name must be 1-10 characters long, can include latin of cyrillic letters (A-z, А-я, case-insensitive), numbers (0-9), and underscores. Please try again.")
   
    # Check if the desk with the new_desk_name already exists
    existing_desk = await orm_select_desk_by_name(session, new_desk_name)
    if existing_desk:
        raise InputError(f"Desk with name: '{new_desk_name}' already exists.")
    
    try:
        await orm_update_desk_name_by_name(session, old_desk_name, new_desk_name)
        return f"Desk with name: {old_desk_name} in room: {room_name} has been renamed to: {new_desk_name}."
    except Exception as e:
        raise e