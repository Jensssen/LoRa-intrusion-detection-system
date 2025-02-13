from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.src.alarm.routes import alarm_router
from app.src.db.main import init_db
from app.src.errors import register_all_errors


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Server is starting ...")
    await init_db()
    yield
    print("Server has been stopped.")


version = "v1"

app = FastAPI(
    title="House alarm API",
    version=version,
    lifespan=life_span

)
register_all_errors(app)

app.include_router(alarm_router, prefix=f"/app/{version}")
