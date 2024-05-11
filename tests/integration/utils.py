from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.logger import Logger
logger = Logger()


TEST_USERS: list[tuple[int, str]] = [
    (123456789, "harry_potter"),
    (234567890, "hermione_granger"),
    (345678901, "ron_weasley"),
    (456789012, "albus_dumbledore"),
    (567890123, "severus_snape"),
    (678901234, "draco_malfoy"),
    (789012345, "tom_riddle"),
    (890123456, "ginny_weasley"),
]


TEST_ROOMS: list[str] = [
    "Gryffindor Room",
    "Slytherin Room",
    "Ravenclaw Room",
    "Hufflepuff Room",
    "Room of Requirement",
    "Great Hall",
]


TEST_DESKS: dict[str, list[str]] = {
    "Gryffindor Room": ["Desk 1", "Desk 2", "Desk 3", "Desk 4"],
    "Slytherin Room": ["Desk 1", "Desk 2", "Desk 3", "Desk 4"],
    "Ravenclaw Room": ["Desk 1", "Desk 2", "Desk 3", "Desk 4"],
    "Hufflepuff Room": ["Desk 1", "Desk 2", "Desk 3", "Desk 4"],
    "Room of Requirement": ["Desk 1", "Desk 2", "Desk 3", "Desk 4"],
    "Great Hall": ["Desk 1", "Desk 2", "Desk 3", "Desk 4"],
}


async def safe_insert(session: AsyncSession, insert_function, data, entity_name: str) -> bool:
    """
    Generic insert function to handle adding entities to the database.
    Logs the operation and commits or rolls back the transaction based on success.
    """
    try:
        logger.info(f"Adding test {entity_name} to the database...")
        await insert_function(session, data)
        await session.commit()
        logger.info(f"{entity_name.capitalize()} have been added to the database.")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"Failed to insert {entity_name}: {e}")
        return False