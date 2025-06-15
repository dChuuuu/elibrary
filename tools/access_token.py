from datetime import datetime, timedelta, timezone
from jose import jwt
from env import SECRET_KEY

ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 5


def get_token(data: dict):
    encode_data = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encode_data.update({"exp": int(expire.timestamp())})
    access_token = jwt.encode(encode_data, SECRET_KEY, algorithm=ALGORITHM)
    return access_token