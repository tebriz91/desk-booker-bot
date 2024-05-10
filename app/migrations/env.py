from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from app.config_data.config import load_config

from app.database.models import (
    User,
    UserRoleAssignment,
    Team,
    TeamTree,
    Waitlist,
    Room,
    Desk,
    DeskAssignment,
    Booking,
)
from app.database.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", load_config().db.url + "?async_fallback=True")

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an asynchronous engine."""
    # Configuration for an async engine
    config.set_main_option("sqlalchemy.url", load_config().db.url)
    async_engine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        echo=True,
    )

    async with async_engine.connect() as connection:
        await connection.run_sync(context.configure,  # Use run_sync to run synchronous Alembic config in async mode
            connection=connection,
            target_metadata=target_metadata,
            compare_server_default=True,
            render_as_batch=True,  # Use this if you're working with SQLite or need batch operations
        )

        async with context.begin_transaction():
            await context.run_migrations_async()  # Ensure migrations are run asynchronously


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        import asyncio
        asyncio.run(run_migrations_online())


if __name__ == "__main__":
    main()