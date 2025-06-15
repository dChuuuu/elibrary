from serializers.readers.serializer import Reader


class ReaderSchema(Reader):

    id: int

    class Config:
        from_attributes = True
