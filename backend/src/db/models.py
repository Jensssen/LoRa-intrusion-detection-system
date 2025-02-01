import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel


class AlarmState(SQLModel, table=True):
    __tablename__ = "alarm_state"
    state_id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4))
    alarm_id: Optional[uuid.UUID] = Field(default=None, foreign_key="alarm.alarm_id", ondelete="CASCADE")

    is_open: bool
    wiggles: bool
    alarm_on: bool
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    # Relationship to Alarm
    alarm: "Alarm" = Relationship(back_populates="states")


class Alarm(SQLModel, table=True):
    __tablename__ = "alarm"
    alarm_id: uuid.UUID = Field(sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4))
    creation_date: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    alarm_location: str

    # Relationship to AlarmState, delete AlarmStates when Alarm is deleted
    states: list["AlarmState"] = Relationship(back_populates="alarm", sa_relationship_kwargs={"cascade": "all, delete"})


def __repr__(self):
    return f"<AlarmState {self.uid}>"
