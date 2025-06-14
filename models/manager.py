from typing import Type
from models.librarian import Librarian
from sqlalchemy.orm import Session
from psycopg2.errors import UniqueViolation
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LibrarianManager:
    async def create(self, email: str, password: str, database: Session) -> Librarian:
        librarian = Librarian(email=email, password=password)
        try:
            database.add(librarian)
            database.commit()
            database.refresh(librarian)
        except IntegrityError as e:
            if isinstance(e.orig, UniqueViolation):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='email already exists')

        return librarian

    async def get(self, email: str, password: str, database: Session) -> Type[Librarian] | None:
        librarian = database.get(Librarian, {'email': email})

        if librarian:
            is_password = pwd_context.verify(password, librarian.password)
            if not is_password:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='wrong pasword')

            return librarian

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='user not found')


