from typing import Type

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import Librarian, Book, Reader, BorrowedBooks
from sqlalchemy.orm import Session
from psycopg2.errors import UniqueViolation
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from serializers.books_logic.serializer import ReaderBookId
from serializers.readers.serializer import Reader as ReaderSerializer
from serializers.books.serializer import Book as BookSerializer
from datetime import date



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LibrarianManager:
    async def create(self, email: str, password: str, database: AsyncSession) -> Librarian:
        async with database as session:
            librarian = Librarian(email=email, password=password)
            session.add(librarian)
            try:

                await session.commit()
                await session.refresh(librarian)
            except IntegrityError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="email already taken"
                )

            return librarian


    async def get(self, email: str, password: str, database: AsyncSession) -> Librarian:

        async with database as session:
            stmt = select(Librarian).where(Librarian.email == email)
            result = await session.execute(stmt)
            librarian = result.scalar_one_or_none()
            if librarian:

                is_password = pwd_context.verify(password, librarian.password)
                if not is_password:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail='wrong pasword')

                return librarian

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='user not found')


class BookManager:

    async def create(self, book: dict, database: AsyncSession) -> Book:
        async with database as session:
            book = Book(**book)
            session.add(book)
            try:

                await session.commit()
                await session.refresh(book)
            except IntegrityError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="isbn already exists"
                )
            return book


    async def get(self, id: int, database: AsyncSession) -> Book:
        async with database as session:
            stmt = select(Book).where(Book.id == id)
            result = await session.execute(stmt)
            book = result.scalar_one_or_none()

            if book:
                return book

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='book not found')


    async def update(self, id: int, database: AsyncSession, **kwargs) -> Book:
        async with database as session:
            stmt = select(Book).where(Book.id == id)
            result = await session.execute(stmt)
            book = result.scalar_one_or_none()

            if book:
                for key, value in kwargs.items():
                    if value is not None:
                        setattr(book, key, value)

                await session.commit()
                await session.refresh(book)

                return book

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='book not found')

    async def delete(self, id: int, database: AsyncSession) -> Book:
        async with database as session:
            stmt = select(Book).where(Book.id == id)
            result = await session.execute(stmt)
            book = result.scalar_one_or_none()
            if book:
                await session.delete(book)
                await session.commit()
                return book
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='book not found')


class ReaderManager:

    async def create(self, reader: dict, database: AsyncSession) -> Reader:
        async with database as session:
            reader = Reader(**reader)
            session.add(reader)
            try:

                await session.commit()
                await session.refresh(reader)

            except IntegrityError as e:
                await session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="email already exists"
                )
            return reader

    async def get(self, id: int, database: AsyncSession) -> Reader:
        async with database as session:
            stmt = select(Reader).where(Reader.id == id)
            result = await session.execute(stmt)
            reader = result.scalar_one_or_none()

            if reader:
                return reader

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='user not found')

    async def update(self, id: int, database: AsyncSession, **kwargs) -> Reader:
        async with database as session:
            stmt = select(Reader).where(Reader.id == id)
            result = await session.execute(stmt)
            reader = result.scalar_one_or_none()

            if reader:
                for key, value in kwargs.items():
                    if value is not None:
                        setattr(reader, key, value)

                await session.commit()
                await session.refresh(reader)

                return reader

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='reader not found')

    async def delete(self, id: int, database: AsyncSession) -> Reader:
        async with database as session:
            stmt = select(Reader).where(Reader.id == id)
            result = await session.execute(stmt)
            reader = result.scalar_one_or_none()
            if reader:
                await session.delete(reader)
                await session.commit()
                return reader
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='reader not found')


class BorrowedBooksManager:

    async def create(self, reader: ReaderSerializer, book: BookSerializer, database: AsyncSession) -> BorrowedBooks:
        async with database as session:
            book_id = book.id

            reader_id = reader.id
            stmt = select(BorrowedBooks).where(BorrowedBooks.reader_id == int(reader_id) and BorrowedBooks.return_date is not None)

            result = await session.execute(stmt)
            borrowed_books = result.scalars().all()
            if len(borrowed_books) >= 3:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='too many borrowed books')

            if int(book.in_stock <= 0):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='books not in stock')

            borrowed_books = BorrowedBooks(reader_id=reader_id, book_id=book_id, borrow_date=date.today())

            session.add(borrowed_books)

            await session.commit()
            await session.refresh(borrowed_books)

            return borrowed_books

    async def return_book(self, borrowed_id: int, database: AsyncSession):
        async with database as session:
            stmt = select(BorrowedBooks).where(BorrowedBooks.id == borrowed_id)
            result = await session.execute(stmt)
            borrowed_book = result.scalar_one_or_none()

            if borrowed_book:
                if borrowed_book.return_date:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail='book already returned')
                stmt = select(Book).where(Book.id == int(borrowed_book.book_id))
                result = await session.execute(stmt)
                book = result.scalar_one_or_none()
                book.in_stock += 1
                await session.commit()
                await session.refresh(book)
                borrowed_book.return_date = date.today()
                await session.commit()
                await session.refresh(borrowed_book)


                return borrowed_book

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='borrowed book not found')

