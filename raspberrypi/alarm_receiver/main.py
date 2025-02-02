import os
import sys
import threading
import time
import asyncio
from queue import Queue

import serial
from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import telegram

load_dotenv()
logger.remove()
logger.add(sys.stdout, level=os.environ['LOGLEVEL'].upper())

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_KEY']
if TELEGRAM_TOKEN is None:
    logger.info(f"TELEGRAM_TOKEN env var not set")
    raise ValueError("No Telegram token provided")

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Create a queue for messages
message_queue = Queue()


def loop2():
    while True:
        data_read = lora.readline().decode('utf-8').strip()
        if data_read != "":
            print(f"Button was pressed: {data_read}")
            # Instead of sending directly, put the message in the queue
            message_queue.put(f"Button was pressed: {data_read}")
        time.sleep(0.1)


def send_lora_message(message: str) -> None:
    lora.write(bytes(message, 'utf-8'))
    print(f"LoRa message was sent: {message}")


async def send_telegram_message(message: str) -> None:
    await bot.send_message(chat_id="396331186", text=message)
    print(f"Telegram message was send: {message}")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    message = message.replace("/hello", "").strip()
    send_lora_message(message)
    await update.message.reply_text(f'🚨🚨 "{message}" send via LoRa🚨🚨')


async def process_queue(application):
    """Process messages from the queue"""
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            await send_telegram_message(message)
        await asyncio.sleep(0.1)


def telegram_setup():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))

    # Add the queue processor to the application
    async def post_init(application):
        application.create_task(process_queue(application))

    app.post_init = post_init
    app.run_polling()


if __name__ == '__main__':
    thread2 = threading.Thread(target=loop2, daemon=True)
    thread2.start()

    telegram_setup()