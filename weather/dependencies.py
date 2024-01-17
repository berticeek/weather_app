from functools import lru_cache

from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import Session

from weather.models.settings import Settings


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    logger.info(f"Loading settings for {settings.environment} environment")
    return settings


def get_session():
    engine = create_engine(get_settings().db_uri)
    with Session(engine) as session:
        yield session
