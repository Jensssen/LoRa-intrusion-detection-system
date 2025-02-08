import os
import sys

import requests
import serial
import telegram.ext as tg_ext
from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes

load_dotenv()
logger.remove()
logger.add(sys.stdout, level=os.environ['LOGLEVEL'].upper())

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_KEY']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
ALARM_API_KEY = os.environ['ALARM_API_KEY']
if TELEGRAM_TOKEN is None:
    logger.info(f"TELEGRAM_TOKEN env var not set")
    raise ValueError("No Telegram token provided")

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)


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
                response_json = response.json()
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


async def listen_to_lora(context: tg_ext.CallbackContext) -> None:
    data_read = lora.readline().decode('utf-8').strip()
    if data_read != "":
        data_read = data_read.replace("||", "|")
        data_read = data_read[1:-1]
        data_read = data_read.split("|")

        ALARMS = [
            {
                "alarm_id": "5f525bd9-0a81-4cba-9fa5-f3fce4937f41",
                "is_open": False,
                "wiggles": False,
                "alarm_on": True,
            }
        ]
        for alarm_status in data_read:
            status = alarm_status.split(",")
            ALARMS[int(status[0])]["is_open"] = bool(int(status[1]))
            ALARMS[int(status[0])]["wiggles"] = bool(int(status[2]))
            ALARMS[int(status[0])]["alarm_on"] = bool(int(status[3]))

        for idx, alarm in enumerate(ALARMS):
            if alarm["is_open"]:
                message = "ALARM! Door is open"
                await context.bot.send_message(TELEGRAM_CHAT_ID, message)
            if alarm["wiggles"]:
                message = "Door wiggles!"
                await context.bot.send_message(TELEGRAM_CHAT_ID, message)

            logger.debug(f"Sending Data to API: {alarm}")
            alarm_handler.send_alarm_state(alarm)


def send_lora_message(message: str) -> None:
    lora.write(bytes(message, 'utf-8'))
    logger.debug(f"LoRa message was sent: {message}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.text.lower()[0:3] == "on:":
        message = update.message.text.lower()
        command, alarm_id = message.split(":")
        send_lora_message(update.message.text.lower())
        await update.message.reply_text(f"Alarm with ID {alarm_id} has been turned ON")
    elif update.message.text.lower()[0:4] == "off:":
        message = update.message.text.lower()
        command, alarm_id = message.split(":")
        send_lora_message(update.message.text.lower())
        await update.message.reply_text(f"Alarm with ID {alarm_id} has been turned OFF")
    else:
        await update.message.reply_text(f"Your Provided command: {update.message.text} is not supported. \n"
                                        f"Please use one of the following commands: \n"
                                        f"on:<alarm_idx>, off:<alarm_idx>")


if __name__ == '__main__':
    app = tg_ext.ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    job_queue = app.job_queue
    job_queue.run_repeating(listen_to_lora, interval=5, first=1)
    app.run_polling()
