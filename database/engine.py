import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base

engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def connection(func):
    """Декоратор для управления сессией базы данных."""
    async def wrapper(*args, **kwargs):
        async with session_maker() as session:
            return await func(session, *args, **kwargs)

    return wrapper


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
