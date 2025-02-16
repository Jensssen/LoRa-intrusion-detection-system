import os
import threading
import time
from datetime import datetime

import pygame
import serial
from gpiozero import Button, LED

from alarm_state import AlarmState

wiggle_button = Button(2)
door_button = Button(3)
alarm_on_off_led = LED(17)
STATUS_FREQUENCY = 15
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "red-alert_nuclear_buzzer-99741.mp3"))
lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)

door = AlarmState(alarm_id=0, is_open=0, is_moving=0, alarm_on=1)
alarm_on_off_led.on()


def alarm_sound_system() -> None:
    """Play alarm sound."""
    while True:
        if wiggle_button.is_pressed or door_button.is_pressed:
            if door.alarm_on:
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pass
                print("Alarm sound played!")
        time.sleep(0.1)


def update_door_moving_state(door_is_moving: int) -> None:
    """
    Compare the new with the current door moving alarm state and update the if necessary.
    It also sends the updated alarm state via LoRa, but only on a state change!
    """
    if door_is_moving == 1:
        if door.is_moving != door_is_moving:
            # Door is moving and was not moving before
            door.door_is_moving()
            send_message(str(door))
    else:
        if door.is_moving != door_is_moving:
            # Door is not moving anymore
            door.door_is_not_moving()
            send_message(str(door))


def update_door_is_open_state(door_is_open: int) -> None:
    """
    Compare the new with the current door open alarm state and update the if necessary.
    It also sends the updated alarm state via LoRa, but only on a state change!
    """
    if door_is_open == 1:
        if door.is_open != door_is_open:
            # Door is now open and was not open before
            door.door_is_open()
            send_message(str(door))
    else:
        if door.is_open != door_is_open:
            # Door is not open anymore
            door.door_is_not_open()
            send_message(str(door))


def door_moving_detection() -> None:
    """Checks constantly if the door is moving."""
    while True:
        if wiggle_button.is_pressed:
            update_door_moving_state(1)
        else:
            update_door_moving_state(0)
        time.sleep(0.1)


def door_open_detection() -> None:
    """Checks constantly if the door is open."""
    while True:
        if door_button.is_pressed:
            update_door_is_open_state(1)
        else:
            update_door_is_open_state(0)
        time.sleep(0.1)


def send_message(message: str) -> None:
    """Send a message via LoRa."""
    print(f"Sending: {message}")
    lora.write(bytes(str(message), 'utf-8'))
    time.sleep(5)


def listen_to_lora() -> None:
    """Constantly listen to LoRa for incoming messages. The message is checked for on/off commands."""
    while True:
        data_read = lora.readline().decode('utf-8').strip()
        if "on:" in data_read.lower():
            alarm_id = data_read.split(":")[-1]
            if int(alarm_id) == door.alarm_id:
                door.turn_alarm_on()
                print("Turned alarm on!")
                send_message(str(door))
                alarm_on_off_led.on()

        elif "off:" in data_read.lower():
            alarm_id = data_read.split(":")[-1]
            if int(alarm_id) == door.alarm_id:
                door.turn_alarm_off()
                print("Turned alarm off!")
                alarm_on_off_led.off()
                send_message(str(door))
        elif data_read != "":
            print(data_read)
        time.sleep(0.1)


def communication_loop() -> None:
    """Send the current alarm state every STATUS_FREQUENCY minutes."""
    last_minute = datetime.now().minute

    while True:
        current_minute = datetime.now().minute
        if current_minute % STATUS_FREQUENCY == 0 and current_minute != last_minute:
            print(f"Send alarm state because timer reached minute {STATUS_FREQUENCY}")
            send_message(str(door))
            last_minute = current_minute
        time.sleep(1)


if __name__ == '__main__':
    print("Start alarm system ...")

    t1 = threading.Thread(target=door_moving_detection)
    t2 = threading.Thread(target=door_open_detection)
    t3 = threading.Thread(target=communication_loop)
    t4 = threading.Thread(target=listen_to_lora)
    t5 = threading.Thread(target=alarm_sound_system)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
