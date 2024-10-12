from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.database.models import Base


def get_engine(
    db_url: str,
    echo: bool = False,
    echo_pool: bool = False,
    pool_size: int = 50,
    max_overflow: int = 10,
    ) -> AsyncEngine:
    """Initialize async engine."""
    engine: AsyncEngine = create_async_engine(
        db_url,
        echo=echo,
        echo_pool=echo_pool,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )
    return engine


def get_session_pool(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Initialize session pool (factory)."""
    session_pool: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=AsyncSession
    )
    return session_pool


async def create_db(engine: AsyncEngine) -> None:
    """Create database tables based on models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    
async def drop_db(engine: AsyncEngine) -> None:
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def drop_db_cascade(engine: AsyncEngine) -> None:
    """Drop all database tables with CASCADE and enums."""
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
