from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import orm_get_room_availability_by_name, orm_update_room_availability_by_name

async def room_availability_toggle_service(
    session: AsyncSession,
    room_name: str
    ) -> str:
    room_name = room_name.strip() #TODO: remove if it's not needed
    # Retrieve room availability by name
    try:
        room_availability = await orm_get_room_availability_by_name(session, room_name)
    except Exception as e:
        return f"Error: {e}"
    # Toggle room availability
    try:
        if room_availability == True:
            await orm_update_room_availability_by_name(session, room_name, False)
            return f"Room: {room_name} is now 🚫unavailable."
        else:
            await orm_update_room_availability_by_name(session, room_name, True)
            return f"Room: {room_name} is now ✅available."
    except Exception as e:
        return f"Error: {e}"