import pytest
import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from database import Base, engine, AsyncSession

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def librarian():
    data = {"email": "email@example.com", "password": "1234Test!"}
    return data

@pytest_asyncio.fixture
async def librarian_login(client, librarian):
    data = librarian
    response = await client.request(method='post', url='/librarians/register', json=data)
    response = await client.request(method='post', url='/librarians/login', json=data)
    return response.json()

@pytest_asyncio.fixture
async def setup_data(client, librarian_login):
    access_token = librarian_login['access_token']

    book_data = {
        "name": "Пример книги",
        "author": "Имя Автора",
        "year_published": 2020,
        "isbn": "978-5-16192-7",
        "in_stock": 10
    }
    book_response = await client.post('/books/add', json=book_data, headers={"Authorization": f'Bearer {access_token}'})
    book = book_response.json()

    reader_data = {"name": "testname", "email": "test@example.com"}
    reader_response = await client.post('/readers/add', json=reader_data, headers={"Authorization": f'Bearer {access_token}'})
    reader = reader_response.json()

    return {"book": book, "reader": reader}


@pytest.mark.asyncio
async def test_book(client, librarian_login, setup_data):
    book_id = setup_data['book']['id']
    reader_id = setup_data['reader']['id']
    access_token = librarian_login['access_token']
    data = {'book_id': book_id,
            'reader_id': reader_id}
    response = await client.post(url='/books/take', json=data, headers={"Authorization": f'Bearer {access_token}'})
    assert response.status_code == 200

    borrowed_id = response.json()['id']
    data = {'borrowed_id': borrowed_id}
    response = await client.post(url=f'/books/return/{borrowed_id}', json=data, headers={"Authorization": f'Bearer {access_token}'})

    assert response.status_code == 200

    data = {'book_id': book_id,
            'reader_id': reader_id}

    for i in range(4):
        response = await client.post(url='/books/take', json=data, headers={"Authorization": f'Bearer {access_token}'})

    assert response.status_code == 400



    data = {
        "name": "Пример книги",
        "author": "Имя Автора",
        "year_published": 2020,
        "isbn": "9718-5-1611192-7",
        "in_stock": 0
    }
    response = await client.post('/books/add', json=data, headers={"Authorization": f'Bearer {access_token}'})
    book_id = response.json()['id']
    data = {'book_id': book_id,
            'reader_id': reader_id}
    response = await client.post(url='/books/take', json=data, headers={"Authorization": f'Bearer {access_token}'})
    assert response.status_code == 400

    data = {
        "name": "Пример книги",
        "author": "Имя Автора",
        "year_published": 2020,
        "isbn": "9718-5-1611192-7",
        "in_stock": 0
    }
    response = await client.post('/books/add', json=data)

    assert response.status_code == 401