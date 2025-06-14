from fastapi import FastAPI, status, Response
from serializers.authentication.serializer import Librarian
from packages.validators.validator import EmailValidator, PasswordValidator
from packages.password_hashing.hasher import hash_password
import json
from models.librarian import Librarian as LibrarianModel
from models.manager import LibrarianManager
from database import SessionLocal, engine
from schemas.librarian import LibrarianSchema
from tools.access_token import get_token
app = FastAPI()


@app.post('/librarians/register', status_code=status.HTTP_201_CREATED, response_model=LibrarianSchema)
async def create_librarian(librarian: Librarian):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    db = SessionLocal()
    await EmailValidator().validate(email)
    await PasswordValidator().validate(password)
    password = await hash_password(password)
    librarian = await LibrarianManager().create(email=email, password=password, database=db)

    return librarian

@app.post('/librarians/login', status_code=status.HTTP_200_OK, response_model=LibrarianSchema)
async def login_librarian(librarian: Librarian):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    db = SessionLocal()
    librarian = await LibrarianManager().get(email=email, password=password, database=db)
    librarian_dict = LibrarianSchema(email=librarian.email).model_dump()
    access_token = get_token(librarian_dict)
    librarian_dict['access_token'] = access_token
    response = librarian_dict
    return response