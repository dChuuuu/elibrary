from sqlalchemy import Column, Integer, String
from database import Base

class Librarian(Base):
    __tablename__ = 'librarians'

    email = Column(String(64), unique=True, primary_key=True)
    password = Column(String())
