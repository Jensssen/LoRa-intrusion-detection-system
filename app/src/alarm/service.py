from typing import Sequence, Type

from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from app.src.db.models import Alarm, AlarmState
from app.src.alarm.schemas import AlarmCreateModel, AlarmStateCreateModel


class AlarmService:

    async def get_alarm(self, alarm_id: str, session: AsyncSession) -> Type[Alarm] | None:
        statement = select(Alarm).where(Alarm.alarm_id == alarm_id)
        result = await session.exec(statement)
        alarm = result.first()
        return alarm if alarm is not None else None

    async def get_last_n_alarm_states(self, alarm_id: str, last_n: int, session: AsyncSession) -> Sequence[AlarmState]:
        statement = select(AlarmState).where(AlarmState.alarm_id == alarm_id).order_by(
            AlarmState.created_at).limit(last_n)

        result = await session.exec(statement)

        return result.all()

    async def get_all_alarms(self, session: AsyncSession) -> Sequence[Alarm]:
        statement = select(Alarm).order_by(desc(Alarm.creation_date))
        result = await session.exec(statement)
        return result.all()

    async def create_alarm(self, alarm_data: AlarmCreateModel, session: AsyncSession) -> Alarm:
        alarm_data = alarm_data.model_dump()
        new_alarm = Alarm(**alarm_data)
        session.add(new_alarm)
        await session.commit()
        return new_alarm

    async def create_alarm_state(self, alarm_state_data: AlarmStateCreateModel, session: AsyncSession) -> AlarmState:
        alarm_state_data = alarm_state_data.model_dump()
        new_alarm_state = AlarmState(**alarm_state_data)
        session.add(new_alarm_state)
        await session.commit()
        return new_alarm_state

    async def delete_alarm(self, alarm_id: str, session: AsyncSession) -> dict[str, str] | None:
        alarm_to_delete = await self.get_alarm(alarm_id, session)

        if alarm_to_delete is not None:
            await session.delete(alarm_to_delete)
            await session.commit()
            return {"message": "Alarm deleted successfully"}
        return None
