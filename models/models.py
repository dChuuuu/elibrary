from sqlalchemy import Column, String, Integer, CheckConstraint, Date
from database import Base

class Librarian(Base):
    __tablename__ = 'librarians'

    email = Column(String(64), unique=True, primary_key=True)
    password = Column(String())


class Book(Base):
    __tablename__ = 'books'


    id = Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    author = Column(String(64), nullable=False)
    year_published = Column(Integer, nullable=True)
    isbn = Column(String, nullable=True, unique=True)
    in_stock = Column(Integer, default=1)

    __table_args__ = (
        CheckConstraint('in_stock >= 0', name='check_quantity_positive'),
    )


class Reader(Base):
    __tablename__ = 'readers'

    id = Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    email = Column(String(64), unique=True)


class BorrowedBooks(Base):
    __tablename__ = 'borrowed_books'
    id = Column(Integer, unique=True, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer)
    reader_id = Column(Integer)
    borrow_date = Column(Date)
    return_date = Column(Date, default=None)
