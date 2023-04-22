import telebot
import config
import sqlite3
from handlers import *
from utils import *


def main():
    logging.info("bot is running")
    initDataBase()
    bot.infinity_polling()


if __name__ == "__main__":
    main()
