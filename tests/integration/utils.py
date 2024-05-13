from typing import List, Tuple, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Base
from app.utils.logger import Logger
logger = Logger()

BOT_CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    "default": {},
    "1": {
        "bot_operation": {
            "advanced_mode": True,
            "num_days": 10,
            "exclude_weekends": False,
            "date_format": "%Y-%m-%d (%a)",
        },
        "bot_advanced_mode": {
            "standard_access_days": 1,
        },
    },
    "2": {
        "bot_operation": {
            "advanced_mode": True,
            "num_days": 5,
            "exclude_weekends": True,
            "date_format": "%m/%d/%Y (%a)",
            "date_format_short": "%m/%d/%Y",
        },
        "bot_advanced_mode": {
            "standard_access_days": 3,
        },
    },
    "3": {
        "bot_operation": {
            "advanced_mode": True,
            "num_days": 7,
            "exclude_weekends": False,
            "date_format": "%d.%m.%Y (%a)",
            "date_format_short": "%d.%m.%Y",
        },
        "bot_advanced_mode": {
            "standard_access_days": 5,
        },
    },
}

# Data Set 1
TEST_USERS_1: List[Tuple[int, str]] = [
    (123456789, "harry_potter"),
    (234567890, "hermione_granger"),
    (345678901, "ron_weasley"),
    (456789012, "albus_dumbledore"),
    (567890123, "severus_snape"),
    (678901234, "draco_malfoy"),
    (789012345, "tom_riddle"),
    (890123456, "ginny_weasley"),
]


TEST_ROOMS_1: List[str] = [
    "Gryffindor Room",
    "Slytherin Room",
    "Ravenclaw Room",
    "Hufflepuff Room",
    "Room of Requirement",
    "Great Hall",
]


TEST_DESKS_1: Dict[str, List[str]] = {
    "Gryffindor Room": [
        "Desk 1", "Desk 2", "Desk 3", "Desk 4", "Desk 5",
    ],
    "Slytherin Room": [
        "Desk 6", "Desk 7", "Desk 8", "Desk 9", "Desk 10",
    ],
    "Ravenclaw Room": [
        "Desk 11", "Desk 12", "Desk 13", "Desk 14", "Desk 15",
    ],
    "Hufflepuff Room": [
        "Desk 16", "Desk 17", "Desk 18", "Desk 19", "Desk 20",
    ],
    "Room of Requirement": [
        "Desk 21", "Desk 22", "Desk 23", "Desk 24", "Desk 25",
    ],
    "Great Hall": [
        "Desk 26", "Desk 27", "Desk 28", "Desk 29", "Desk 30",
    ],
}


# Data Set 2
TEST_USERS_2: List[Tuple[int, str]] = [
    (223456789, "james_potter"),
    (334567890, "lily_potter"),
    (445678901, "sirius_black"),
    (556789012, "remus_lupin"),
    (667890123, "peter_pettigrew"),
    (778901234, "narcissa_malfoy"),
    (889012345, "lucius_malfoy"),
    (990123456, "bellatrix_lestrange"),
]


TEST_ROOMS_2: List[str] = [
    "Dumbledore's Office",
    "Snape's Dungeon",
    "Moaning Myrtle's Bathroom",
    "Forbidden Forest",
    "Hagrid's Hut",
    "Astronomy Tower",
]


TEST_DESKS_2: Dict[str, List[str]] = {
    "Dumbledore's Office": ["Desk 31", "Desk 32", "Desk 33", "Desk 34", "Desk 35"],
    "Snape's Dungeon": ["Desk 36", "Desk 37", "Desk 38", "Desk 39", "Desk 40"],
    "Moaning Myrtle's Bathroom": ["Desk 41", "Desk 42", "Desk 43", "Desk 44", "Desk 45"],
    "Forbidden Forest": ["Desk 46", "Desk 47", "Desk 48", "Desk 49", "Desk 50"],
    "Hagrid's Hut": ["Desk 51", "Desk 52", "Desk 53", "Desk 54", "Desk 55"],
    "Astronomy Tower": ["Desk 56", "Desk 57", "Desk 58", "Desk 59", "Desk 60"],
}


# Data Set 3
TEST_USERS_3: List[Tuple[int, str]] = [
    (323456789, "arthur_weasley"),
    (434567890, "molly_weasley"),
    (545678901, "bill_weasley"),
    (656789012, "charlie_weasley"),
    (767890123, "percy_weasley"),
    (878901234, "fred_weasley"),
    (989012345, "george_weasley"),
    (190123456, "fleur_delacour"),
]


TEST_ROOMS_3: List[str] = [
    "Weasley Kitchen",
    "Weasley Living Room",
    "The Burrow Attic",
    "The Burrow Basement",
    "The Burrow Garden",
    "The Burrow Garage",
]


TEST_DESKS_3: Dict[str, List[str]] = {
    "Weasley Kitchen": ["Desk 61", "Desk 62", "Desk 63", "Desk 64", "Desk 65"],
    "Weasley Living Room": ["Desk 66", "Desk 67", "Desk 68", "Desk 69", "Desk 70"],
    "The Burrow Attic": ["Desk 71", "Desk 72", "Desk 73", "Desk 74", "Desk 75"],
    "The Burrow Basement": ["Desk 76", "Desk 77", "Desk 78", "Desk 79", "Desk 80"],
    "The Burrow Garden": ["Desk 81", "Desk 82", "Desk 83", "Desk 84", "Desk 85"],
    "The Burrow Garage": ["Desk 86", "Desk 87", "Desk 88", "Desk 89", "Desk 90"],
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