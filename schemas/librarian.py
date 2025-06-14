from pydantic import BaseModel


class LibrarianSchema(BaseModel):

    email: str
    access_token: str = None

    class Config:
        from_attributes = True


