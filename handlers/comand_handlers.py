import logging
import telebot
import config
import time
import utils.database_utils
from utils.account_manager import AccountManager




BOT = telebot.TeleBot(token=config.TOKEN)
ACCOUNT_MANAGER = AccountManager()

@BOT.message_handler(commands=['start'])
def start(message):
	"""Обрабатывает команду пользователя на добавление товара"""
	BOT.send_message(chat_id=message.chat.id, text="Здравствуйте. Для использования функционала бота "
														 "вам необходимо авторизоваться")
	time.sleep(1)
	mes = BOT.send_message(chat_id=message.chat.id, text="Введите код работника или администратора:")
	BOT.register_next_step_handler(mes, auth)


def auth(message):
	"""Авторизует пользователя по ключу"""
	access_level = utils.database_utils.check_auth(message.text)
	if access_level == -1:
		mes = BOT.send_message(chat_id=message.chat.id, text="Введен неверный код. Введите код повторно:")
		BOT.register_next_step_handler(mes, auth)
		return
	BOT.send_message(chat_id=message.chat.id,
					 text=f"Вы вошли в систему как {'администратор' if access_level else 'работник'}")
	ACCOUNT_MANAGER.auth(message.from_user.id, access_level)



@BOT.message_handler(commands=['add'])
def add_product(message):
	"""Обрабатывает команду пользователя на добавление товара"""
	pass


@BOT.message_handler(commands=['setv'])
def set_value_of_product(message):
	"""Обрабатывает команду пользователя на изменение цены товара"""
	pass


@BOT.message_handler(commands=['seta'])
def set_amount_of_product(message):
	"""Обрабатывает команду пользователя на изменение количества товара"""
	pass


@BOT.message_handler(commands=['del'])
def del_product(message):
	"""Обрабатывает команду пользователя на удаление товара"""
	pass


@BOT.message_handler(commands=['add'])
def info_of_product(message):
	"""Обрабатывает команду пользователя на получение информации о товаре"""
	pass

