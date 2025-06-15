from pydantic import BaseModel


class ReaderBookId(BaseModel):
    reader_id: int
    book_id: int