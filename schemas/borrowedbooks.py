from serializers.books_logic.serializer import ReaderBookId


class BorrowedBooksSchema(ReaderBookId):

    id: int

    class Config:
        from_attributes = True
