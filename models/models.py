from sqlalchemy import Column, String, Integer, CheckConstraint
from database import Base

class Librarian(Base):
    __tablename__ = 'librarians'

    email = Column(String(64), unique=True, primary_key=True)
    password = Column(String())


class Book(Base):
    __tablename__ = 'books'


    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    author = Column(String(64), nullable=False)
    year_published = Column(Integer, nullable=True)
    isbn = Column(String, nullable=True, unique=True)
    in_stock = Column(Integer, default=1)

    __table_args__ = (
        CheckConstraint('in_stock > 0', name='check_quantity_positive'),
    )