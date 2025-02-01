from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.src.alarm.routes import alarm_router
from backend.src.db.main import init_db
from backend.src.db.models import Alarm, AlarmState
from backend.src.errors import register_all_errors


@asynccontextmanager
async def life_span(app: FastAPI):
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
