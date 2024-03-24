from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_available_rooms


async def generate_available_rooms_list(session: AsyncSession) -> List[str]:
    rooms_orm_obj = await orm_select_available_rooms(session)
    return [room.name for room in rooms_orm_obj]