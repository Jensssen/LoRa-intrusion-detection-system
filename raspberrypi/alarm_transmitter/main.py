import threading
import time
from datetime import datetime

import pygame
import serial
from gpiozero import Button

wiggle_button = Button(2)
door_button = Button(3)
STATUS_FREQUENCY = 15
pygame.mixer.init()
pygame.mixer.music.load("red-alert_nuclear_buzzer-99741.mp3")
lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)

ALARM_IDS = ["5f525bd9-0a81-4cba-9fa5-f3fce4937f41"]

ALARMS = [
    {
        "alarm_id": 0,
        "is_open": False,
        "wiggles": False,
        "alarm_on": True,
        "name": "Cellar"
    }
]


def alarm_sound_system() -> None:
    while True:
        if wiggle_button.is_pressed or door_button.is_pressed:
            print("Alarm started")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass
            print("Alarm stopped")
        time.sleep(0.1)


def cellar_wiggle_detection() -> None:
    alarm_idx = 0

    while True:
        if wiggle_button.is_pressed:
            ALARMS[alarm_idx]["wiggles"] = 1
            send_message(alarm_state_to_str(ALARMS[alarm_idx]))
        else:
            ALARMS[alarm_idx]["wiggles"] = 0
        time.sleep(0.1)


def cellar_door_open_detection() -> None:
    alarm_idx = 0
    while True:
        if door_button.is_pressed:
            ALARMS[alarm_idx]["is_open"] = 1
            send_message(alarm_state_to_str(ALARMS[alarm_idx]))
        else:
            ALARMS[alarm_idx]["is_open"] = 0
        time.sleep(0.1)


def alarm_state_to_str(alarm: dict) -> str:
    return f"|{alarm['alarm_id']},{int(alarm['is_open'])},{int(alarm['wiggles'])},{int(alarm['alarm_on'])}|"


def send_message(message: str) -> None:
    print(f"Sending: {message}")
    print("\n")
    lora.write(bytes(str(message), 'utf-8'))
    time.sleep(5)


def listen_to_lora() -> None:
    data_read = lora.readline().decode('utf-8').strip()

    if "on:" in data_read.lower():
        alarm_id = data_read.split(":")[-1]
        try:
            ALARMS[int(alarm_id)]["alarm_on"] = 1
            print(f"ALARM_STATE of {alarm_id} changed to {ALARMS[int(alarm_id)]['alarm_on']}")
        except KeyError:
            print(f"Provided alarm id was incorrect: {alarm_id}")
    elif "off:" in data_read.lower():
        alarm_id = data_read.split(":")[-1]
        try:
            ALARMS[int(alarm_id)]["alarm_on"] = 0
            print(f"ALARM_STATE changed to {ALARMS[int(alarm_id)]['alarm_on']}")
        except KeyError:
            print(f"Provided alarm id was incorrect: {alarm_id}")

    elif data_read != "":
        print(data_read)


def communication_loop() -> None:
    last_minute = datetime.now().minute

    while True:
        message = ""
        for alarm in ALARMS:
            message += f"|{alarm['alarm_id']},{alarm['is_open']},{alarm['wiggles']},{alarm['alarm_on']}|"

        current_minute = datetime.now().minute
        if current_minute % STATUS_FREQUENCY == 0 and current_minute != last_minute:
            send_message(message)
            last_minute = current_minute
        listen_to_lora()
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
    t4 = threading.Thread(target=alarm_sound_system)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
