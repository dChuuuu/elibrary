from pydantic import BaseModel


class LibrarianSchema(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True