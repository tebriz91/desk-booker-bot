from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_get_desk_availability_by_name, orm_update_desk_availability_by_name

async def desk_availability_toggle_service(
    session: AsyncSession,
    room_name: str,
    desk_name: str
    ) -> str:
    desk_name = desk_name.strip() #TODO: remove if it's not needed
    # Retrieve desk availability by name
    try:
        desk_availability = await orm_get_desk_availability_by_name(session, desk_name)
    except Exception as e:
        return f"Error: {e}"
    # Toggle desk availability
    try:
        if desk_availability == True:
            await orm_update_desk_availability_by_name(session, desk_name, False)
            return f"Desk: {desk_name} in room: {room_name} is now 🚫unavailable."
        else:
            await orm_update_desk_availability_by_name(session, desk_name, True)
            return f"Desk: {desk_name} in room: {room_name} is now ☑️available."
    except Exception as e:
        return f"Error: {e}"