from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_delete_room_by_name

async def room_delete_service(
    session: AsyncSession,
    room_name: str
    ) -> str:
    room_name = room_name.strip()
    try:
        await orm_delete_room_by_name(session, room_name)
        return f"Room with name: {room_name} has been deleted."
    except Exception as e:
        return f"Error: {e}"