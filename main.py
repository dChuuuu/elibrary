from fastapi import FastAPI, status, Response, Depends
from fastapi.security import OAuth2PasswordBearer

from schemas.book import BookSchema
from serializers.authentication.serializer import Librarian
from serializers.books.serializer import Book, BookUpdate
from packages.validators.validator import EmailValidator, PasswordValidator
from packages.password_hashing.hasher import hash_password
import json
from models.models import Librarian as LibrarianModel
from models.manager import LibrarianManager, BookManager
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

@app.post('/secured')
async def secured_endpoint(token: str = Depends(authenticate)):
    return {'message': 'successful'}

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
    book = await BookManager().update(id, db, **updated_book)

    return book

@app.delete('/books/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int, token: str = Depends(authenticate)):
    db = AsyncSession()
    book = await BookManager().delete(id, db)

