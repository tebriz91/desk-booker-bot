from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_queries import orm_select_available_rooms


async def generate_available_rooms_list(session: AsyncSession) -> List[str]:
    rooms_orm_obj = await orm_select_available_rooms(session)
    return [room.name for room in rooms_orm_obj]


# Returns a list of tuples with room_id and room_name
async def generate_available_rooms_as_list_of_tuples(session: AsyncSession) -> List[Tuple[int, str]]:
    rooms_orm_obj = await orm_select_available_rooms(session)
    return [(room.id, room.name) for room in rooms_orm_obj]