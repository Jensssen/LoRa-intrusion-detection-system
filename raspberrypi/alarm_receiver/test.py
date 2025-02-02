import sys
import threading
import time

import serial
from decouple import config
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS, timeout=1)


def loop1():
    while True:
        print("Loop 1")
        time.sleep(1)


def loop2():
    while True:
        data_read = lora.readline()
        print(data_read)
        time.sleep(0.1)


def send_alarm():
    message = "Hello World!"
    lora.write(bytes(message, 'utf-8'))
    print(f"LoRa message was sent: {message}")


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    send_alarm()
    await update.message.reply_text(f'🚨🚨🚨🚨 Message send via LoRa')


def telegram_setup():
    logger.remove()
    logger.add(sys.stdout, level=config("LOGLEVEL", cast=str).upper())

    TELEGRAM_TOKEN = config(f"TELEGRAM_BOT_KEY", cast=str)
    if TELEGRAM_TOKEN is None:
        logger.info(f"TELEGRAM_TOKEN env var not set")
        raise ValueError("No Telegram token provided")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("hello", hello))
    app.run_polling()


if __name__ == '__main__':
    thread1 = threading.Thread(target=loop1, daemon=True)
    thread2 = threading.Thread(target=loop2, daemon=True)

    thread1.start()
    thread2.start()

    telegram_setup()
