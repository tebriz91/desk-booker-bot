"""
This is a configuration module for testing. It copies the configuration module from the main application and adjusts it for testing purposes. The main difference is in the load_config function, which allows to override configuration values during testing so we can test different scenarios without changing environment variables.
"""
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, List, Optional, Union


# Attempt to load environment variables from .env file
try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv())
except ImportError:
    pass


# Define a type alias for file paths
_PathLike = Union[os.PathLike[str], Path, str]


# Function to fetch environment variables with optional type casting
def get_env(value: str, cast_to_type: Optional[str] = None) -> Any:
    """
    Fetches environment variables with optional type casting.
    
    :param value: The name of the environment variable.
    :param cast_to_type: The type to cast the value to. Supports 'int', 'bool', 'str', and 'json'.
    :return: The environment variable value, possibly cast to a specified type.
    """
    v = os.getenv(value)
    if v is not None:
        if cast_to_type == "json":
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error parsing JSON for environment variable {value}: {e}")
        elif cast_to_type == "int":
            try:
                return int(v)
            except ValueError as e:
                raise ValueError(f"Error casting to int for environment variable {value}: {e}")
        elif cast_to_type == "bool":
            return v.lower() in ("true", "1", "t", "yes")
        else:
            return v
    return v


# Database configuration
@dataclass(slots=True)
class DBConfig:
    uri: str
    name: str
    date_format: Optional[str] = field(default="%Y-%m-%d")
    host: Optional[str] = field(default=None)
    port: Optional[int] = field(default=None)
    user: Optional[str] = field(default=None)
    password: Optional[str] = field(default=None)

    @property
    def url(self) -> str:
        """
        Returns the database URL based on the provided configuration in .env file.
        """
        if 'sqlite' in self.uri:
            # Check if '.db' extension is already included in the name
            db_extension = '' if self.name.endswith('.db') else '.db'
            return f'{self.uri}///{self.name}{db_extension}' # returns: sqlite+aiosqlite:///db_name.db
        elif 'postgresql' in self.uri:
            return f'{self.uri}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}' # returns: postgresql+asyncpg://login:password@localhost:5432/db_name
        else:
            raise ValueError("Unsupported database type")


# Bot authentication configuration
@dataclass(slots=True)
class BotConfig:
    token: str
    admins: List[int]


# Bot operation configuration
@dataclass(slots=True)
class BotOperationConfig:
    num_days: Optional[int] = field(default=5)
    exclude_weekends: Optional[bool] = field(default=True)
    timezone: Optional[str] = field(default="UTC")
    country_code: Optional[str] = field(default=None)
    date_format: Optional[str] = field(default="%d.%m.%Y (%a)")
    date_format_short: Optional[str] = field(default="%d.%m.%Y")
    advanced_mode: Optional[bool] = field(default=False)
    
    def to_dict(self) -> dict:
        """Convert the BotOperationConfig dataclass instance into a dictionary."""
        return asdict(self)
 

# Bot advanced mode configuration
@dataclass(slots=True)
class BotAdvancedModeConfig:
    standard_access_days: Optional[int] = field(default=1)

    def to_dict(self) -> dict:
        return asdict(self)

    
# Redis configuration
@dataclass(slots=True)
class RedisConfig:
    host: Optional[str] = field(default=None)
    port: Optional[int] = field(default=None)

    @property
    def dict(self) -> Optional[dict]:
        if not self.host and not self.port:
            return None

        return {"host": self.host, "port": self.port}


# Main configuration aggregator
@dataclass(slots=True)
class Config:
    db: DBConfig
    bot: BotConfig
    bot_operation: BotOperationConfig
    bot_advanced_mode: BotAdvancedModeConfig
    redis: RedisConfig


    @staticmethod
    def root_dir() -> Path:
        return Path(__file__).resolve().parent.parent.parent


    @classmethod
    def path(cls, *paths: _PathLike, base_path: Optional[_PathLike] = None) -> str:
        if base_path is None:
            base_path = cls.root_dir()

        return os.path.join(base_path, *paths)


def load_config(overrides: Optional[dict] = None) -> Config:
    # Default values loaded from environment
    config = Config(
        db=DBConfig(
            uri=get_env("DB_URI"),
            name=get_env("DB_NAME"),
            date_format=get_env("DB_DATE_FORMAT"),
            host=get_env("DB_HOST"),
            port=get_env("DB_PORT", "int"),
            user=get_env("DB_USER"),
            password=get_env("DB_PASSWORD"),
        ),
        bot=BotConfig(
            token=get_env("BOT_TOKEN"),
            admins=get_env("BOT_ADMINS", "json"),
        ),
        bot_operation=BotOperationConfig(
            num_days=get_env("NUM_DAYS", "int"),
            exclude_weekends=get_env("EXCLUDE_WEEKENDS", "bool"),
            timezone=get_env("TIMEZONE"),
            country_code=get_env("COUNTRY_CODE"),
            date_format=get_env("DATE_FORMAT"),
            date_format_short=get_env("DATE_FORMAT_SHORT"),
            advanced_mode=get_env("ADVANCED_MODE", "bool"),
        ),
        bot_advanced_mode=BotAdvancedModeConfig(
            standard_access_days=get_env("STANDARD_ACCESS_DAYS", "int"),
        ),
        redis=RedisConfig(
            host=get_env("REDIS_HOST"),
            port=get_env("REDIS_PORT", "int"),
        ),
    )
    # Apply overrides if provided
    if overrides:
        for section, values in overrides.items():
            section_config = getattr(config, section)
            updated_values = {**section_config.to_dict(), **values}
            setattr(config, section, type(section_config)(**updated_values))
    
    return config