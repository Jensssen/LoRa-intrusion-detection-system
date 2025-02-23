import os
import sys

import serial
import telegram.ext as tg_ext
from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
import re

from alarm_handler import AlarmHandler

load_dotenv()
logger.remove()
logger.add(sys.stdout, level=os.environ['LOGLEVEL'].upper())

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_KEY']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
ALARM_API_KEY = os.environ['ALARM_API_KEY']
if TELEGRAM_TOKEN is None:
    logger.info("TELEGRAM_TOKEN env var not set")
    raise ValueError("No Telegram token provided")

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)

alarm_handler = AlarmHandler(ALARM_API_KEY)
ALARMS = ["5f525bd9-0a81-4cba-9fa5-f3fce4937f41"]
ALARM_NAMES = ["Cellar"]


def is_valid_binary_pattern(s: str) -> bool:
    """Check if the given string is a valid alarm state pattern."""
    pattern = r"^(0|[1-9]\d*)(,(0|1)){3}(,(0|[1-9]\d*)(,(0|1)){3})*$"
    return bool(re.fullmatch(pattern, s))


async def listen_to_lora(context: tg_ext.CallbackContext) -> None:
    """Listen to incoming LoRa messages and send the alarm state to the API."""
    data_read = lora.readline().decode('utf-8').strip()
    if data_read != "":
        if is_valid_binary_pattern(data_read):
            alarm_id, is_open, is_moving, is_on = data_read.split(",")[0:4]
            alarm = {
                "alarm_id": ALARMS[int(alarm_id)],
                "is_open": bool(int(is_open)),
                "wiggles": bool(int(is_moving)),
                "alarm_on": bool(int(is_on)),
            }
            logger.debug(f"Sending Data to API: {alarm}")
            alarm_handler.send_alarm_state(alarm)

            if bool(int(is_open)):
                message = f"{ALARM_NAMES[int(alarm_id)]} door is open!"
                await context.bot.send_message(TELEGRAM_CHAT_ID, message)
            if bool(int(is_moving)):
                message = f"{ALARM_NAMES[int(alarm_id)]} door is moving!"
                await context.bot.send_message(TELEGRAM_CHAT_ID, message)


def send_lora_message(message: str) -> None:
    """Send LoRa message."""
    lora.write(bytes(message, 'utf-8'))
    logger.debug(f"LoRa message was sent: {message}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming telegram messages. The message is checked for on/off commands."""
    user_first_name = str(update.message.chat.first_name)
    if user_first_name == os.environ['TELEGRAM_USER_NAME']:
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
