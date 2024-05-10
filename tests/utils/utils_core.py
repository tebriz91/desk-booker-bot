import os
from pathlib import Path
from types import SimpleNamespace

from alembic.config import Config
from sqlalchemy import make_url, text, URL
from sqlalchemy.ext.asyncio import create_async_engine

from app.config_data.config import load_config


MAIN_USER_ID = 1111111111
OTHER_USER_ID = 2222222222
NONE_USER_ID = None
INVALID_USER_ID = 'some_str'
ABSENT_IN_DB_USER_ID = 9090909090
USER_ID_WITH_TRACKER_LIMIT = 5555555555
LANG_CODE = ...
TRACKER_ID = str(1)
ACTION_ID = 1
ACTION_NAME = 'action_test'
CATEGORY_ID = 1
CATEGORY_NAME = 'category_test'
POSTGRES_DEFAULT_DB = "postgres"

PROJECT_PATH = Path(__file__).parent.parent.resolve()


def make_alembic_config(cmd_opts, base_path: str = PROJECT_PATH) -> Config:
    # Replace path to alembic.ini file to absolute
    if not os.path.isabs(cmd_opts.config):
        cmd_opts.config = os.path.join(base_path, cmd_opts.config)

    config = Config(file_=cmd_opts.config, ini_section=cmd_opts.name,
                    cmd_opts=cmd_opts)

    # Replace path to alembic folder to absolute
    alembic_location = config.get_main_option('script_location')
    if not os.path.isabs(alembic_location):
        config.set_main_option('script_location',
                               os.path.join(base_path, alembic_location))
    if cmd_opts.pg_url:
        print(cmd_opts.pg_url)
        config.set_main_option('sqlalchemy.url', cmd_opts.pg_url)

    return config


def alembic_config_from_url(database_url: str | None = None) -> Config:
    """
    Provides Python object, representing alembic.ini file.
    """
    cmd_options = SimpleNamespace(
        config='alembic.ini', name='alembic', pg_url=database_url,
        raiseerr=False, x=None,
    )

    return make_alembic_config(cmd_options)


async def create_database(url: str):
    """Create a new database in the PostgreSQL server.

    This function is used to create a new PostgreSQL database using the specified URL.
    It checks if the database already exists and, if not, creates the new database.

    :param url: The database URL.
    :return: None
    """
    url_object = make_url(url)
    database_name = url_object.database
    dbms_url = url_object.set(database=POSTGRES_DEFAULT_DB)
    engine = create_async_engine(dbms_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        c = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{database_name}'")
        )
        database_exists = c.scalar() == 1

    if database_exists:
        await drop_database(url_object)

    async with engine.connect() as conn:
        await conn.execute(
            text(f'CREATE DATABASE "{database_name}"')
        )
    await engine.dispose()


async def drop_database(url: str | URL):
    """Drop a database from the PostgreSQL server.

    This function is used to drop a PostgreSQL database based on the specified URL.
    It disconnects users and drops the database.

    :param url: str: The database URL.
    :return: None
    """
    url_object = make_url(url)
    dbms_url = url_object.set(database=POSTGRES_DEFAULT_DB)
    engine = create_async_engine(dbms_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disconnect_users = """
        SELECT pg_terminate_backend(pg_stat_activity.{pid_column})
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{database}'
          AND {pid_column} <> pg_backend_pid();
        """.format(
            pid_column="pid",
            database=url_object.database,
        )
        await conn.execute(text(disconnect_users))
        await conn.execute(text(f'DROP DATABASE "{url_object.database}"'))
