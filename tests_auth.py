import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from database import Base, engine

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
    data = {"email": "email@example.com", "password": ""}
    return data

@pytest.mark.asyncio
async def test_librarian_auth(client, librarian):
    response = await client.post('/librarians/register', json=librarian)
    assert response.status_code == 400

    librarian['password'] = "password"
    response = await client.post('/librarians/register', json=librarian)
    assert response.status_code == 400

    librarian['password'] += '1'
    response = await client.post('/librarians/register', json=librarian)
    assert response.status_code == 400

    librarian['password'] += 'P'
    response = await client.post('/librarians/register', json=librarian)
    assert response.status_code == 400

    librarian['password'] += '!'
    librarian['email'] = 'email'
    response = await client.post('/librarians/register', json=librarian)
    assert response.status_code == 400

    librarian['email'] = 'email@example.com'
    response = await client.post('/librarians/register', json=librarian)
    assert response.status_code == 201

    response = await client.post('/librarians/login', json=librarian)
    assert response.status_code == 200
    assert response.json()['access_token'] is not None
