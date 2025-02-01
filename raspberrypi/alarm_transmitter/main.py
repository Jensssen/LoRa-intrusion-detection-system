import time
from typing import Callable

import RPi.GPIO as GPIO
import serial

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)


# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#
# while True:
#     if GPIO.input(26) == GPIO.HIGH:
#         print("Button was pushed!")
#         b = bytes(str(1), 'utf-8')
#         lora.write(b)
#     else:
#         print("Button was not pushed!")
#     time.sleep(2)


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
                          bouncetime=200)  # Debounce time in milliseconds


def cleanup():
    GPIO.cleanup()


def send_alarm(channel):
    print(f"Pin {channel} is now HIGH!")
    print("Button was pushed!")
    b = bytes(str(1), 'utf-8')
    lora.write(b)


if __name__ == "__main__":
    try:
        PIN = 26
        setup_gpio_monitor(PIN, send_alarm)

        # Keep the script running
        print(f"Monitoring GPIO {PIN}. Press CTRL+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting program")
    finally:
        cleanup()
