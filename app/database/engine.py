from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.database.models import Base


engine = None  # Declare engine as a global variable to be initialized later
session_maker = None  # Same for session_maker


def initialize_engine(db_url, echo=True):
    """
    Initialize the async engine and session maker using the database URL.
    This function should be called with configuration data from outside.
    """
    global engine, session_maker
    engine = create_async_engine(db_url, echo=echo)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def get_session_maker():
    """
    Returns the session maker. Ensures that the session maker is initialized.
    This function can be called to obtain the session maker without directly
    accessing the global variable, providing a layer of abstraction.
    """
    if session_maker is None:
        raise Exception("Database engine and session maker have not been initialized. Call initialize_engine first.")
    return session_maker


async def create_db():
    """
    Create database tables based on models.
    Requires the engine to be initialized first.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    
async def drop_db():
    """
    Drop all database tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def drop_db_cascade():
    async with engine.begin() as conn:
        # Reflecting all tables from the database
        await conn.run_sync(Base.metadata.reflect)

        # Dropping each table manually with CASCADE
        for table_name in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"DROP TABLE IF EXISTS {table_name.name} CASCADE;"))
        
        # Dropping all enums
        enum_types_to_drop = [
            "userrole",
            "weekdays",
        ]
        for enum_type in enum_types_to_drop:
            await conn.execute(text(f"DROP TYPE IF EXISTS {enum_type};"))