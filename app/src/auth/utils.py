import logging
import uuid
from datetime import datetime, timedelta

import jwt

from app.src.config import Config

ACCESS_TOKEN_EXPIRY = 3600


def create_access_token(data: dict, expiry: timedelta = None, refresh: bool = False):
    """
    Create access token using RS256.

    Args:
        data: Data to be included in the token.
        expiry: How long the token should be valid.
        refresh: If a refresh token should be provided.
    """
    with open(Config.JWT_PRIVATE_KEY, "r") as key_file:
        private_key = key_file.read()

    payload = {"data": data,
               "exp": datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)),
               "jti": str(uuid.uuid4()), "refresh": refresh
    }

    token = jwt.encode(payload=payload, key=private_key, algorithm=Config.JWT_ALGORITHM)

    return token


def decode_token(token: str) -> dict | None:
    with open(Config.JWT_PUBLIC_KEY, "r") as key_file:
        public_key = key_file.read()
    try:
        token_data = jwt.decode(jwt=token, key=public_key, algorithms=[Config.JWT_ALGORITHM])
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None


if __name__ == '__main__':
    token = create_access_token(data={"email": "test@gmail.com"}, expiry=timedelta(days=10000))
    decode = decode_token(token)
    print(decode)
    print(token)
