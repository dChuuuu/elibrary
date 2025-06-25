from fastapi import FastAPI, status, Depends
from sqlalchemy import select
from schemas.book import BookSchema
from schemas.borrowedbooks import BorrowedBooksSchema
from schemas.reader import ReaderSchema
from serializers.authentication.serializer import Librarian
from serializers.books.serializer import Book, BookUpdate
from serializers.readers.serializer import Reader, ReaderUpdate
from packages.validators.validator import EmailValidator, PasswordValidator
from packages.password_hashing.hasher import hash_password
from serializers.books_logic.serializer import ReaderBookId
from models.models import Book as BookModel, BorrowedBooks as BorrowedBooksModel
from models.manager import LibrarianManager, BookManager, ReaderManager, BorrowedBooksManager
from database import get_db, AsyncSession
from schemas.librarian import LibrarianSchema, LibrarianJWTSchema
from tools.access_token import get_token
from tools.authentication import authenticate

app = FastAPI()


@app.post('/librarians/register', status_code=status.HTTP_201_CREATED, response_model=LibrarianSchema)
async def create_librarian(librarian: Librarian, db: AsyncSession = Depends(get_db)):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    await EmailValidator().validate(email)
    await PasswordValidator().validate(password)
    password = await hash_password(password)
    librarian = await LibrarianManager().create(email=email, password=password, session=db)

    return librarian

@app.post('/librarians/login', status_code=status.HTTP_200_OK, response_model=LibrarianJWTSchema)
async def login_librarian(librarian: Librarian, db: AsyncSession = Depends(get_db)):
    librarian = librarian.model_dump()
    email = librarian['email']
    password = librarian['password']
    librarian = await LibrarianManager().get(email=email, password=password, session=db)
    librarian_dict = LibrarianSchema(email=librarian.email).model_dump()
    access_token = get_token(librarian_dict)
    librarian_dict['access_token'] = access_token
    response = librarian_dict

    return response

@app.post('/books/add', status_code=status.HTTP_201_CREATED, response_model=BookSchema)
async def create_book(book: Book, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):
    book = book.model_dump()
    book = await BookManager().create(book=book, session=db)

    return book

@app.get('/books/{id}', status_code=status.HTTP_200_OK, response_model=BookSchema)
async def get_book(id: int, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):
    book = await BookManager().get(id=id, session=db)
    return book

@app.patch('/books/{id}', status_code=status.HTTP_200_OK, response_model=BookSchema)
async def update_book(id: int, updated_book: BookUpdate, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):
    updated_book = updated_book.model_dump()
    try:
        await EmailValidator().validate(updated_book['email'])
    except KeyError:
        pass
    book = await BookManager().update(id, db, **updated_book)



    return book

@app.delete('/books/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):

    await BookManager().delete(id, db)

@app.post('/readers/add', status_code=status.HTTP_201_CREATED, response_model=ReaderSchema)
async def create_reader(reader: Reader, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):
    reader = reader.model_dump()
    await EmailValidator().validate(reader['email'])

    reader = await ReaderManager().create(reader=reader, session=db)

    return reader

@app.get('/readers/{id}', status_code=status.HTTP_200_OK, response_model=ReaderSchema)
async def get_book(id: int, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):

    reader = await ReaderManager().get(id=id, session=db)

    return reader

@app.patch('/readers/{id}', status_code=status.HTTP_200_OK, response_model=ReaderSchema)
async def update_reader(id: int, updated_reader: ReaderUpdate, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):

    updated_reader = updated_reader.model_dump()
    try:
        await EmailValidator().validate(updated_reader['email'])
    except KeyError:
        pass
    reader = await ReaderManager().update(id, db, **updated_reader)

    return reader

@app.delete('/readers/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(id: int, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):

    await ReaderManager().delete(id, db)


@app.post('/books/take', status_code=status.HTTP_200_OK, response_model=BorrowedBooksSchema)
async def take_book(data: ReaderBookId, db: AsyncSession = Depends(get_db), token: str = Depends(authenticate)):
    data = data.model_dump()
    book_id = data['book_id']
    reader_id = data['reader_id']
    book = await BookManager().get(book_id, db)
    reader = await ReaderManager().get(reader_id, db)
    borrowed_book = await BorrowedBooksManager().create(reader, book, db)
    book.in_stock -= 1
    await BookManager().update(book.id, db, in_stock=book.in_stock)

    return borrowed_book

@app.post('/books/return/{borrowed_id}', status_code=status.HTTP_200_OK)
async def return_book(borrowed_id: int, db: AsyncSession = Depends(get_db)):

    borrowed_book = await BorrowedBooksManager().return_book(borrowed_id, db)
    return borrowed_book

@app.get('/books', status_code=status.HTTP_200_OK)
async def get_books(db: AsyncSession = Depends(get_db)):

    stmt = select(BookModel)
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books

@app.get('/books/get_borrowed_book/{reader_id}', status_code=status.HTTP_200_OK)
async def get_borrowed_book(reader_id: int, db: AsyncSession = Depends(get_db), token = Depends(authenticate)):

    stmt = select(BorrowedBooksModel).where(BorrowedBooksModel.reader_id == reader_id)
    result = await db.execute(stmt)
    borrowed_books = result.scalars().all()
    borrowed_books_list = []
    for borrowed_book in borrowed_books:
        if borrowed_book.return_date is not None:
            pass
        else:
            stmt = select(BookModel).where(BookModel.id == int(borrowed_book.book_id))
            result = await db.execute(stmt)
            book = result.scalar_one_or_none()
            borrowed_books_list.append(book)

    return borrowed_books_list







