import os
import sys

import serial
import telegram.ext as tg_ext
from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes

TELEGRAM_CHAT_ID = "396331186"

load_dotenv()
logger.remove()
logger.add(sys.stdout, level=os.environ['LOGLEVEL'].upper())

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_KEY']
ALARM_API_KEY = os.environ['ALARM_API_KEY']
if TELEGRAM_TOKEN is None:
    logger.info(f"TELEGRAM_TOKEN env var not set")
    raise ValueError("No Telegram token provided")

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)


async def listen_to_lora(context: tg_ext.CallbackContext) -> None:
    data_read = lora.readline().decode('utf-8').strip()
    if data_read != "":
        logger.debug(f"raw message: {data_read}")
        await context.bot.send_message(TELEGRAM_CHAT_ID, data_read)


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


def main() -> None:
    app = tg_ext.ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    job_queue = app.job_queue
    job_queue.run_repeating(listen_to_lora, interval=5, first=1)
    app.run_polling()


if __name__ == '__main__':
    main()
