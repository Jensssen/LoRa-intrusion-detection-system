from dataclasses import dataclass


@dataclass
class AlarmState:
    alarm_id: int = 0
    is_open: int = 0
    is_moving: int = 0
    alarm_on: int = 1

    def __str__(self) -> str:
        return f"{self.alarm_id},{self.is_open},{self.is_moving},{self.alarm_on}"

    def __repr__(self) -> str:
        return f"{self.alarm_id},{self.is_open},{self.is_moving},{self.alarm_on}"

    def door_is_moving(self) -> None:
        self.is_moving = 1

    def door_is_not_moving(self) -> None:
        self.is_moving = 0

    def door_is_open(self) -> None:
        self.is_open = 1

    def door_is_not_open(self) -> None:
        self.is_open = 0

    def turn_alarm_on(self) -> None:
        self.alarm_on = 1

    def turn_alarm_off(self) -> None:
        self.alarm_on = 0
