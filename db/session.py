from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str


settings = Settings()

engine = create_async_engine(settings.DB_URL, echo=True)
