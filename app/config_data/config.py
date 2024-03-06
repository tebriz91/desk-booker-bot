import json
import os
from dataclasses import dataclass, field
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
def get_env(value: str, cast_to_type: bool = False) -> Any:
    v = os.getenv(value)
    if cast_to_type and v:
        return json.loads(v)
    return v

# Database configuration
@dataclass(frozen=True, slots=True)
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
        if "sqlite" in self.uri:
            return self.uri.format(self.name)
        return self.uri.format(
            self.user, self.password, self.host, self.port, self.name
        )

# Bot authentication configuration
@dataclass(frozen=True, slots=True)
class BotConfig:
    token: str
    admins: List[int]

# Bot operation configuration
@dataclass(frozen=True, slots=True)
class BotOperationConfig:
    num_days: Optional[int] = field(default=5)
    exclude_weekends: Optional[bool] = field(default=True)
    timezone: Optional[str] = field(default="UTC")
    country_code: Optional[str] = field(default=None)
    date_format: Optional[str] = field(default="%d.%m.%Y (%a)")
    date_format_short: Optional[str] = field(default="%d.%m.%Y")

# Redis configuration
@dataclass(frozen=True, slots=True)
class RedisConfig:
    host: Optional[str] = field(default=None)
    port: Optional[int] = field(default=None)

    @property
    def dict(self) -> Optional[dict]:
        if not self.host and not self.port:
            return None

        return {"host": self.host, "port": self.port}

# Main configuration aggregator
@dataclass(frozen=True, slots=True)
class Config:
    db: DBConfig
    bot: BotConfig
    bot_operation: BotOperationConfig
    redis: RedisConfig

    @staticmethod
    def root_dir() -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @classmethod
    def path(cls, *paths: _PathLike, base_path: Optional[_PathLike] = None) -> str:
        if base_path is None:
            base_path = cls.root_dir()

        return os.path.join(base_path, *paths)

# Function to load configuration from environment variables
def load_config() -> Config:
    return Config(
        db=DBConfig(
            uri=get_env("DB_URI"),
            name=get_env("DB_NAME"),
            date_format=get_env("DB_DATE_FORMAT"),
            host=get_env("DB_HOST"),
            port=get_env("DB_PORT", True),
            user=get_env("DB_USER"),
            password=get_env("DB_PASSWORD")
        ),
        bot=BotConfig(
            token=get_env("BOT_TOKEN"),
            admins=get_env("BOT_ADMINS", True)
        ),
        bot_operation=BotOperationConfig(
            num_days=get_env("NUM_DAYS"),
            exclude_weekends=get_env("EXCLUDE_WEEKENDS"),
            timezone=get_env("TIMEZONE"),
            country_code=get_env("COUNTRY_CODE"),
            date_format=get_env("DATE_FORMAT"),
            date_format_short=get_env("DATE_FORMAT_SHORT")
        ),
        redis=RedisConfig(
            host=get_env("REDIS_HOST"),
            port=get_env("REDIS_PORT")
        ),
    )