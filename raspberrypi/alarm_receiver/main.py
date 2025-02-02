import sys

import serial
from decouple import config
from loguru import logger
from telegram import Bot

logger.remove()
logger.add(sys.stdout, level=config("LOGLEVEL", cast=str))

TELEGRAM_TOKEN = config(f"TELEGRAM_BOT_KEY", cast=str)
if TELEGRAM_TOKEN is None:
    logger.info(f"TELEGRAM_TOKEN env var not set")
    raise ValueError("No Telegram token provided")

bot = Bot(token=TELEGRAM_TOKEN)


async def process_alarm() -> None:
    await bot.send_message(chat_id="telegram_id", text=f"🚨🚨🚨🚨")


def read_lora(port='/dev/ttyS0', baudrate=9600):
    try:
        with serial.Serial(port, baudrate, parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS) as lora:
            print("Listening for LoRa messages...")
            while True:
                try:
                    # Read a line from the LoRa module
                    data_read = lora.readline().decode('utf-8').strip()
                    if data_read:
                        print(f"Received: {data_read}")
                        process_alarm()
                except serial.SerialException as e:
                    print(f"Serial error: {e}")
                    break
                except UnicodeDecodeError as e:
                    print(f"Decode error: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break

    except serial.SerialException as e:
        print(f"Could not open serial port: {e}")


if __name__ == '__main__':
    read_lora()




