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

# lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
#                      bytesize=serial.EIGHTBITS, timeout=1)

TELEGRAM_CHAT_ID = "396331186"

bot = telegram.Bot(token=TELEGRAM_TOKEN)

message_queue = Queue()


# def lora_receiver_loop() -> None:
#     while True:
#         data_read = lora.readline().decode('utf-8').strip()
#         if data_read != "":
#             logger.debug(f"raw message: {data_read}")
#             logger.debug(f"Button was pressed: {data_read}")
#             message_queue.put(f"Button was pressed: {data_read}")
#         time.sleep(0.1)


def send_lora_message(message: str) -> None:
    # lora.write(bytes(message, 'utf-8'))
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


if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("on", alarm_on))
    app.add_handler(CommandHandler("off", alarm_off))



    logger.info("Polling ...")
    app.run_polling(poll_interval=5)
    print("hi")
