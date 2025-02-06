import time
from datetime import datetime
from typing import Callable

import RPi.GPIO as GPIO
import serial

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)

ALARMS = [{
    "alarm_id": "5f525bd9-0a81-4cba-9fa5-f3fce4937f41",
    "is_open": False,
    "wiggles": False,
    "alarm_on": True,
    "name": "Cellar"
}]

for alarm in ALARMS:
    print(f"Alarm {alarm['name']} is on: {alarm['alarm_on']}")
    print(f"Alarm {alarm['name']} door open: {alarm['is_open']}")
    print(f"Alarm {alarm['name']} door wiggles: {alarm['wiggles']}")


def setup_gpio_monitor(pin_number: int, callback_function: Callable) -> None:
    """
    Set up GPIO pin monitoring with a callback function

    Args:
        pin_number (int): The GPIO pin to monitor (BCM numbering)
        callback_function: Function to call when pin goes high
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin_number, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(pin_number, GPIO.RISING,
                          callback=callback_function,
                          bouncetime=2000)  # Debounce time in milliseconds


def cleanup() -> None:
    GPIO.cleanup()


def send_message(message: str) -> None:
    print(f"Sending: {message}")
    b = bytes(str(message), 'utf-8')
    lora.write(b)


def wiggle_button_pressed(channel: int, alarm_idx: int = 0) -> None:
    """Called if door wiggles."""
    print(f"Pin {channel} is now HIGH!")
    print(f"Door wiggles")
    alarm = ALARMS[alarm_idx]
    message = f"||{alarm['alarm_id']},{int(alarm['is_open'])},1,{int(alarm['alarm_on'])}||"
    send_message(message)


def door_button_pressed(channel: int, alarm_idx: int = 0) -> None:
    """Called if door is open."""
    print(f"Pin {channel} is now HIGH!")
    print(f"Door is open!")
    alarm = ALARMS[alarm_idx]
    message = f"||{alarm['alarm_id']},1,{int(alarm['wiggles'])},{int(alarm['alarm_on'])}||"
    send_message(message)


if __name__ == "__main__":
    DOOR_WIGGLE_BUTTON = 26
    DOOR_OPEN_BUTTON = 16
    STATUS_FREQUENCY = 1

    try:
        # Setup first alarm button that checks if door wiggles
        setup_gpio_monitor(DOOR_WIGGLE_BUTTON, wiggle_button_pressed)

        # Setup second alarm button that checks if door is open
        setup_gpio_monitor(DOOR_OPEN_BUTTON, door_button_pressed)

        last_minute = datetime.now().minute

        while True:
            data_read = lora.readline().decode('utf-8').strip()

            if data_read == "ON":
                ALARMS[0]["alarm_on"] = True
                print(f"ALARM_STATE changed to {ALARMS[0]['alarm_on']}")
            elif data_read == "OFF":
                ALARMS[0]["alarm_on"] = False
                print(f"ALARM_STATE changed to {ALARMS[0]['alarm_on']}")
            elif data_read != "":
                print(data_read)

            current_minute = datetime.now().minute
            if current_minute % STATUS_FREQUENCY == 0 and current_minute != last_minute:
                alarm = ALARMS[0]
                message = (f"||{alarm['alarm_id']},"
                           f"{int(alarm['is_open'])},"
                           f"{int(alarm['wiggles'])},"
                           f"{int(alarm['alarm_on'])}||")
                send_message(message)
                last_minute = current_minute
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nExiting program")
    finally:
        cleanup()