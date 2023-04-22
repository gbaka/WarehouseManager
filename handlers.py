import telebot
import config

if __name__ == "handlers":
	bot = telebot.TeleBot(token=config.TOKEN)


@bot.message_handler(commands=['add'])
def add_product(message):
	"""
	Обрабатывает команду пользователя на добавление товара
	"""
	pass


@bot.message_handler(commands=['setv'])
def set_value_of_product(message):
	"""
	Обрабатывает команду пользователя на изменение цены товара
	"""
	pass


@bot.message_handler(commands=['seta'])
def set_amount_of_product(message):
	"""
	Обрабатывает команду пользователя на изменение количества товара
	"""
	pass


@bot.message_handler(commands=['del'])
def del_product(message):
	"""
	Обрабатывает команду пользователя на удаление товара
	"""
	pass


@bot.message_handler(commands=['add'])
def info_of_product(message):
	"""
	Обрабатывает команду пользователя на получение информации о товаре
	"""
	pass

