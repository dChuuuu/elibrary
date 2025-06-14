from passlib.context import CryptContext
from fastapi import HTTPException, status

# Создаем контекст с алгоритмом bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def hash_password(password):
    hashed_password = pwd_context.hash(password)
    pwd_context.verify(password, hashed_password)
    return hashed_password
