from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from app.src.auth.utils import decode_token
from app.src.errors import InvalidToken


class AccessTokenBearer(HTTPBearer):
    pass

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        if not self.token_valid(token):
            raise InvalidToken()
        return decode_token(token)

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return True if token_data is not None else False
