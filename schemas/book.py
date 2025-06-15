from serializers.books.serializer import Book


class BookSchema(Book):

    id: int

    class Config:
        from_attributes = True
