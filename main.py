import telebot
import config
import sqlite3
from handlers.comand_handlers import *
from utils.database_manager import *



def main():
    logging.info("bot is running")
    BOT.infinity_polling()


if __name__ == "__main__":
    main()

