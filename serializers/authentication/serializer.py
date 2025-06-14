from pydantic import BaseModel

class Librarian(BaseModel):
    email: str
    password: str
