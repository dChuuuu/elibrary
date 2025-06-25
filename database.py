from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from env import POSTGRES_USER_PASSWORD, DATABASE_USER, DATABASE_USER_PASSWORD, DATABASE_NAME

DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_USER_PASSWORD}@localhost/{DATABASE_NAME}'

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSession() as session:
        yield session
