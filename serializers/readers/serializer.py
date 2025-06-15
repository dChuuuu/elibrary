from pydantic import BaseModel
from typing import Optional

class Reader(BaseModel):
    name: str
    email: str

class ReaderUpdate(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    year_published: Optional[int] = None
    isbn: Optional[str] = None
    in_stock: Optional[int] = None