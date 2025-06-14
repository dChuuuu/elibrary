from sqlalchemy import Column, Integer, String
from database import Base

class Librarian(Base):
    __tablename__ = 'librarians'

    id = Column(Integer, primary_key=True)
    email = Column(String(64), unique=True)
    password = Column(String())
