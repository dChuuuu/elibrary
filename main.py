from fastapi import FastAPI, status, Response, Depends
from fastapi.security import OAuth2PasswordBearer

from schemas.book import BookSchema
from schemas.borrowedbooks import BorrowedBooksSchema
from schemas.reader import ReaderSchema
from serializers.authentication.serializer import Librarian
from serializers.books.serializer import Book, BookUpdate
from serializers.readers.serializer import Reader, ReaderUpdate
from packages.validators.validator import EmailValidator, PasswordValidator
from packages.password_hashing.hasher import hash_password
from serializers.books_logic.serializer import ReaderBookId
import json
from models.models import Librarian as LibrarianModel
from models.manager import LibrarianManager, BookManager, ReaderManager, BorrowedBooksManager
from database import AsyncSession, engine
from schemas.librarian import LibrarianSchema, LibrarianJWTSchema
from tools.access_token import get_token
from tools.authentication import authenticate



app = FastAPI()


@app.post('/librarians/register', status_code=status.HTTP_201_CREATED, response_model=LibrarianSchema)
async def create_librarian(librarian: Librarian):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    db = AsyncSession()
    await EmailValidator().validate(email)
    await PasswordValidator().validate(password)
    password = await hash_password(password)
    librarian = await LibrarianManager().create(email=email, password=password, database=db)

    return librarian

@app.post('/librarians/login', status_code=status.HTTP_200_OK, response_model=LibrarianJWTSchema)
async def login_librarian(librarian: Librarian):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    db = AsyncSession()
    librarian = await LibrarianManager().get(email=email, password=password, database=db)
    librarian_dict = LibrarianSchema(email=librarian.email).model_dump()
    access_token = get_token(librarian_dict)
    librarian_dict['access_token'] = access_token
    response = librarian_dict

    return response

@app.post('/books/add', status_code=status.HTTP_201_CREATED, response_model=BookSchema)
async def create_book(book: Book, token: str = Depends(authenticate)):
    book = book.model_dump()
    db = AsyncSession()
    book = await BookManager().create(book=book, database=db)

    return book

@app.get('/books/{id}', status_code=status.HTTP_200_OK, response_model=BookSchema)
async def get_book(id: int, token: str = Depends(authenticate)):
    db = AsyncSession()
    book = await BookManager().get(id=id, database=db)
    return book

@app.patch('/books/{id}', status_code=status.HTTP_200_OK, response_model=BookSchema)
async def update_book(id: int, updated_book: BookUpdate, token: str = Depends(authenticate)):
    db = AsyncSession()
    updated_book = updated_book.model_dump()
    try:
        await EmailValidator().validate(updated_book['email'])
    except KeyError:
        pass
    book = await BookManager().update(id, db, **updated_book)



    return book

@app.delete('/books/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int, token: str = Depends(authenticate)):
    db = AsyncSession()
    await BookManager().delete(id, db)

@app.post('/readers/add', status_code=status.HTTP_201_CREATED, response_model=ReaderSchema)
async def create_reader(reader: Reader, token: str = Depends(authenticate)):
    reader = reader.model_dump()
    await EmailValidator().validate(reader['email'])
    db = AsyncSession()
    reader = await ReaderManager().create(reader=reader, database=db)

    return reader

@app.get('/readers/{id}', status_code=status.HTTP_200_OK, response_model=ReaderSchema)
async def get_book(id: int, token: str = Depends(authenticate)):
    db = AsyncSession()
    reader = await ReaderManager().get(id=id, database=db)

    return reader

@app.patch('/readers/{id}', status_code=status.HTTP_200_OK, response_model=ReaderSchema)
async def update_reader(id: int, updated_reader: ReaderUpdate, token: str = Depends(authenticate)):
    db = AsyncSession()
    updated_reader = updated_reader.model_dump()
    try:
        await EmailValidator().validate(updated_reader['email'])
    except KeyError:
        pass
    reader = await ReaderManager().update(id, db, **updated_reader)

    return reader

@app.delete('/readers/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int, token: str = Depends(authenticate)):
    db = AsyncSession()
    await ReaderManager().delete(id, db)


@app.post('/books/take', status_code=status.HTTP_200_OK, response_model=BorrowedBooksSchema)
async def take_book(data: ReaderBookId, token: str = Depends(authenticate)):
    data = data.model_dump()
    book_id = data['book_id']
    reader_id = data['reader_id']
    db = AsyncSession()
    book = await BookManager().get(book_id, db)
    reader = await ReaderManager().get(reader_id, db)
    borrowed_book = await BorrowedBooksManager().create(reader, book, db)
    book.in_stock -= 1
    await BookManager().update(book.id, db, in_stock=book.in_stock)

    return borrowed_book

@app.post('/books/return/{borrowed_id}', status_code=status.HTTP_200_OK)
async def return_book(borrowed_id: int):
    db = AsyncSession()
    borrowed_book = await BorrowedBooksManager().return_book(borrowed_id, db)
    return borrowed_book




