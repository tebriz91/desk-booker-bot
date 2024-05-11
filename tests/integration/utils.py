from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base
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
    "Gryffindor Room": [
        "Desk 1",
        "Desk 2",
        "Desk 3",
        "Desk 4",
        "Desk 5",
    ],
    "Slytherin Room": [
        "Desk 6",
        "Desk 7",
        "Desk 8",
        "Desk 9",
        "Desk 10",
    ],
    "Ravenclaw Room": [
        "Desk 11",
        "Desk 12",
        "Desk 13",
        "Desk 14",
        "Desk 15",
    ],
    "Hufflepuff Room": [
        "Desk 16",
        "Desk 17",
        "Desk 18",
        "Desk 19",
        "Desk 20",
    ],
    "Room of Requirement": [
        "Desk 21",
        "Desk 22",
        "Desk 23",
        "Desk 24",
        "Desk 25",
    ],
    "Great Hall": [
        "Desk 26",
        "Desk 27",
        "Desk 28",
        "Desk 29",
        "Desk 30",
    ],
}


async def safe_insert(session: AsyncSession, insert_function, data, entity_name: str) -> bool:
    """
    Generic insert function to handle adding entities to the database.
    This version does not commit or rollback, as these actions will be managed externally.
    """
    try:
        await insert_function(session, data)
        logger.info(f"{entity_name.capitalize()} have been added to the database.")
        return True
    except Exception as e:
        logger.error(f"Failed to insert {entity_name}: {e}")
        return False


async def create_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def truncate_db_cascade(session: AsyncSession):
    if session.in_transaction():
        await session.rollback()  # Ensure no transactions are open
    async with session.begin():
        await session.execute(text("SET CONSTRAINTS ALL DEFERRED;"))  # Optional
        for table_name in reversed(Base.metadata.sorted_tables):
            await session.execute(text(f"TRUNCATE TABLE {table_name.name} CASCADE;"))