import asyncio
import os
import sys
import threading
import time
from queue import Queue

import requests
import serial
import telegram
from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
logger.remove()
logger.add(sys.stdout, level=os.environ['LOGLEVEL'].upper())

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_KEY']
ALARM_API_KEY = os.environ['ALARM_API_KEY']
if TELEGRAM_TOKEN is None:
    logger.info(f"TELEGRAM_TOKEN env var not set")
    raise ValueError("No Telegram token provided")

if ALARM_API_KEY is None:
    logger.info(f"ALARM_API_KEY env var not set")
    raise ValueError("No Alarm API key provided")


lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)

TELEGRAM_CHAT_ID = "396331186"

bot = telegram.Bot(token=TELEGRAM_TOKEN)

message_queue = Queue()


class AlarmHandler:

    def __init__(self, token: str) -> None:
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self.url = "https://house-alarm.memomate.me/app/v1/"

    def send_alarm_state(self, data: dict) -> None:
        """
        Send the current alarm state to the alarm API.

        Args:
            data: Dictionary holding the create_alarm_state (see docs)
        """
        try:
            response = requests.post(self.url + "create_alarm_state", json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.debug("Response Status Code:", response.status_code)

            try:
                response_json = response.json()  # Try parsing JSON response
                logger.error("Response JSON:", response_json)
            except ValueError:
                logger.error("Response is not in JSON format:", response.text)

        except requests.exceptions.Timeout:
            logger.error("Request timed out. The server may be unreachable.")
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to the server. Check if the server is running.")
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            logger.error(f"An error occurred: {err}")


alarm_handler = AlarmHandler(ALARM_API_KEY)


def lora_receiver_loop() -> None:
    while True:
        data_read = lora.readline().decode('utf-8').strip()
        if data_read != "":
            logger.debug(f"raw message: {data_read}")
            data = data_read.split("||")[1]

            logger.debug(f"Button was pressed: {data}")
            message_queue.put(f"Button was pressed: {data_read}")

        time.sleep(0.1)


def send_lora_message(message: str) -> None:
    lora.write(bytes(message, 'utf-8'))
    logger.debug(f"LoRa message was sent: {message}")


async def send_telegram_message(message: str) -> None:
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    logger.debug(f"Telegram message was send: {message}")


async def alarm_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    send_lora_message("ON")
    await update.message.reply_text('Alarm has been turned ON')


async def alarm_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    send_lora_message("OFF")
    await update.message.reply_text('Alarm has been turned off')


async def process_queue(application):
    """Process messages from the queue"""
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            await send_telegram_message(message)
        await asyncio.sleep(0.1)


def telegram_setup():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("on", alarm_on))
    app.add_handler(CommandHandler("off", alarm_off))

    # Add the queue processor to the application
    async def post_init(application):
        application.create_task(process_queue(application))

    app.post_init = post_init
    app.run_polling()


if __name__ == '__main__':
    lora_thread = threading.Thread(target=lora_receiver_loop, daemon=True)
    lora_thread.start()

    telegram_setup()
