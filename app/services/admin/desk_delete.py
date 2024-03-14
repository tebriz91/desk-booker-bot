from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_select_desk_id_by_name, orm_delete_desk_by_id

async def desk_delete_service(
    session: AsyncSession,
    desk_name: str,
    room_name: str
    ) -> str:
    # Retrieve desk_id by desk_name
    try:
        desk_id = await orm_select_desk_id_by_name(session, desk_name)
    except Exception as e:
        return f"Error: {e}"
    
    try:
        await orm_delete_desk_by_id(session, desk_id)
        return f"Desk: {desk_name} in room: {room_name} has been deleted."
    except Exception as e:
        return f"Error: {e}"