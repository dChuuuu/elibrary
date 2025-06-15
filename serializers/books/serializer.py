from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    name: str
    author: str
    year_published: int
    isbn: str
    in_stock: int

class BookUpdate(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    year_published: Optional[int] = None
    isbn: Optional[str] = None
    in_stock: Optional[int] = None