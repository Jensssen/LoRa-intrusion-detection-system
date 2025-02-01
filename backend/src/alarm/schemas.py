import uuid
from datetime import datetime

from pydantic import BaseModel


class AlarmState(BaseModel):
    state_id: uuid.UUID
    alarm_id: uuid.UUID
    is_open: bool
    wiggles: bool
    created_at: datetime
    alarm_on: bool


class AlarmStateCreateModel(BaseModel):
    alarm_id: uuid.UUID
    is_open: bool
    wiggles: bool
    alarm_on: bool


class Alarm(BaseModel):
    alarm_id: uuid.UUID
    creation_date: datetime
    alarm_location: str


class AlarmCreateModel(BaseModel):
    alarm_location: str
