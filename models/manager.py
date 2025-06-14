from models.librarian import Librarian
from sqlalchemy.orm import Session
from psycopg2.errors import UniqueViolation
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

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