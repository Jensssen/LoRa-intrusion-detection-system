from typing import List

from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.src.alarm.schemas import AlarmCreateModel, Alarm, AlarmState, AlarmStateCreateModel
from backend.src.alarm.service import AlarmService
from backend.src.db.main import get_session
from backend.src.errors import AlarmNotFound

alarm_router = APIRouter()
alarm_service = AlarmService()


@alarm_router.get("/get_all_alarms", response_model=List[Alarm], status_code=status.HTTP_200_OK)
async def get_all_alarms(session: AsyncSession = Depends(get_session)):
    alarms = await alarm_service.get_all_alarms(session=session)
    return alarms


@alarm_router.post("/create_alarm", response_model=Alarm, status_code=status.HTTP_201_CREATED)
async def create_alarm(alarm_data: AlarmCreateModel, session: AsyncSession = Depends(get_session)):
    new_alarm = await alarm_service.create_alarm(alarm_data=alarm_data, session=session)
    return new_alarm


@alarm_router.delete("/delete_alarm/{alarm_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_alarm(alarm_id: str, session: AsyncSession = Depends(get_session)):
    deleted_alarm = await alarm_service.delete_alarm(alarm_id=alarm_id, session=session)
    if deleted_alarm is None:
        raise AlarmNotFound()
    else:
        return deleted_alarm


@alarm_router.post("/create_alarm_state", response_model=AlarmState, status_code=status.HTTP_201_CREATED)
async def create_alarm_state(alarm_state_data: AlarmStateCreateModel, session: AsyncSession = Depends(get_session)):
    new_alarm_state = await alarm_service.create_alarm_state(alarm_state_data=alarm_state_data, session=session)
    return new_alarm_state


@alarm_router.get("/get_alarm_states/{alarm_id}/", response_model=List[AlarmState], status_code=status.HTTP_200_OK)
async def get_alarm_states(alarm_id: str, n: int = 100, session: AsyncSession = Depends(get_session)):
    alarms = await alarm_service.get_last_n_alarm_states(alarm_id=alarm_id, last_n=n, session=session)
    return alarms
