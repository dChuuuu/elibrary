from datetime import datetime, timedelta
from jose import jwt
from env import SECRET_KEY

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5


def get_token(data: dict):
    encode_data = data.copy()
    expire = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp": expire})
    access_token = jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)
    return access_token