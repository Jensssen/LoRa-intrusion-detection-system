import threading
import time
from datetime import datetime

import serial
from gpiozero import Button

wiggle_button = Button(2)
door_button = Button(3)
STATUS_FREQUENCY = 1
lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)
ALARMS = [
    {
        "alarm_id": "5f525bd9-0a81-4cba-9fa5-f3fce4937f41",
        "is_open": False,
        "wiggles": False,
        "alarm_on": True,
        "name": "Cellar"
    },
    {
        "alarm_id": "1212121212121212121212121212121",
        "is_open": False,
        "wiggles": False,
        "alarm_on": True,
        "name": "Apartment"
    }
]


def cellar_wiggle_detection():
    alarm_idx = 0

    while True:
        if wiggle_button.is_pressed:
            ALARMS[alarm_idx]["wiggles"] = True
            send_message(alarm_state_to_str(ALARMS[alarm_idx]))
        else:
            ALARMS[alarm_idx]["wiggles"] = False
        time.sleep(0.1)


def cellar_door_open_detection():
    alarm_idx = 0
    while True:
        if door_button.is_pressed:
            ALARMS[alarm_idx]["is_open"] = True
            send_message(alarm_state_to_str(ALARMS[alarm_idx]))
        else:
            ALARMS[alarm_idx]["is_open"] = False
        time.sleep(0.1)


def alarm_state_to_str(alarm: dict):
    return f"|{alarm['alarm_id']},{int(alarm['is_open'])},{int(alarm['wiggles'])},{int(alarm['alarm_on'])}|"


def send_message(message: str) -> None:
    print(f"Sending: {message}")
    print("\n")
    lora.write(bytes(str(message), 'utf-8'))
    time.sleep(1)


def communication_loop():
    last_minute = datetime.now().minute

    while True:
        message = ""
        for alarm in ALARMS:
            message += f"|{alarm['alarm_id']},{int(alarm['is_open'])},{int(alarm['wiggles'])},{int(alarm['alarm_on'])}|"

        current_minute = datetime.now().minute
        if current_minute % STATUS_FREQUENCY == 0 and current_minute != last_minute:
            send_message(message)
            last_minute = current_minute
            print(message)

        time.sleep(0.1)


if __name__ == '__main__':
    print("Start alarm system ...")

    for alarm in ALARMS:
        print(f"Alarm {alarm['name']} is on: {alarm['alarm_on']}")
        print(f"Alarm {alarm['name']} door open: {alarm['is_open']}")
        print(f"Alarm {alarm['name']} door wiggles: {alarm['wiggles']}")
        print("\n")

    t1 = threading.Thread(target=cellar_wiggle_detection)
    t2 = threading.Thread(target=cellar_door_open_detection)
    t3 = threading.Thread(target=communication_loop)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
