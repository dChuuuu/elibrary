from fastapi import FastAPI, status, Response
from serializers.authentication.serializer import Librarian
from packages.validators.validator import EmailValidator, PasswordValidator
from packages.password_hashing.hasher import hash_password
import json
from models.librarian import Librarian as LibrarianModel
from models.manager import LibrarianManager
from database import SessionLocal, engine
from schemas.librarian import LibrarianSchema

app = FastAPI()


@app.post('/librarians/create', status_code=status.HTTP_201_CREATED, response_model=LibrarianSchema)
async def create_librarian(librarian: Librarian):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    await EmailValidator().validate(email)
    await PasswordValidator().validate(password)
    password = await hash_password(password)
    db = SessionLocal()
    librarian = await LibrarianManager().create(email=email, password=password, database=db)

    return librarian
    #return Response(content=json.dumps(librarian), media_type='application/json')
    #return Response(content=librarian.__str__(), media_type='application/json')
