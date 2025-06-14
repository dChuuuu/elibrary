from pydantic import BaseModel


class LibrarianSchema(BaseModel):

    email: str

    class Config:
        from_attributes = True

class LibrarianJWTSchema(LibrarianSchema):

    access_token: str | None

