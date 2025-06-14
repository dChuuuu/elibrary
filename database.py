from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from env import POSTGRES_USER_PASSWORD, DATABASE_USER, DATABASE_USER_PASSWORD, DATABASE_NAME

SQLALCHEMY_DATABASE_URL = f'postgresql+psycopg2://{DATABASE_USER}:{DATABASE_USER_PASSWORD}@localhost/{DATABASE_NAME}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
