from typing import Any

from fastapi import FastAPI, status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ExceptionHandler


class AlarmException(Exception):
    """This is the base class for all alarm errors"""
    pass


class AlarmNotFound(AlarmException):
    pass


class InvalidToken(AlarmException):
    """User has provided an invalid or expired token"""

    pass


def create_exception_handler(
        status_code: int, initial_detail: Any
) -> ExceptionHandler:
    async def exception_handler(request: Request, exc: AlarmException) -> JSONResponse:
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI) -> None:
    app.add_exception_handler(
        AlarmNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Alarm Not Found",
                "error_code": "alarm_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid Or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token",
            },
        ),
    )
