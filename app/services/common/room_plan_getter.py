from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import (
    orm_select_room_plan_by_room_name,
    orm_select_room_plan_by_room_id,
)


async def get_room_plan_by_room_name(
    session: AsyncSession,
    room_name: str,
    ) -> str:
    try:
        room_plan = await orm_select_room_plan_by_room_name(session, room_name)
        return room_plan
    except Exception as e:
        return f"Error: {e}"
    

async def get_room_plan_by_room_id(
    session: AsyncSession,
    room_id: int,
    ) -> str:
    try:
        room_plan = await orm_select_room_plan_by_room_id(session, room_id)
        return room_plan
    except Exception as e:
        return f"Error: {e}"