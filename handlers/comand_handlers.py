import telebot
import config
import handlers.helpers as helpers
from utils.database_manager import DatabaseManager

BOT = telebot.TeleBot(token=config.TOKEN)
DATABASE_MANAGER = DatabaseManager(config.db_name)


@BOT.message_handler(
    commands=['start'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['start'])
)
def start(message):
    """Обрабатывает команду пользователя на добавление товара"""
    BOT.send_message(chat_id=message.chat.id, text="Здравствуйте. Для использования функционала бота "
                                                   "вам необходимо авторизоваться")
    mes = BOT.send_message(chat_id=message.chat.id, text="Введите код работника или администратора:")
    BOT.register_next_step_handler(mes, auth)


def auth(message):
    """Авторизует пользователя по ключу"""
    access_level = DATABASE_MANAGER.check_auth(message.text)
    if access_level == 0:
        mes = BOT.send_message(chat_id=message.chat.id, text="Введен неверный код. Введите код повторно:")
        BOT.register_next_step_handler(mes, auth)
        return
    BOT.send_message(chat_id=message.chat.id,
                     text=f"Вы вошли в систему как {'работник' if access_level == 1 else 'администратор'}")
    helpers.ACCOUNT_MANAGER.auth(message.from_user.id, access_level)
    helpers.ACCOUNT_MANAGER.show()


@BOT.message_handler(
    commands=['add'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['add'])
)
def add_product(message):
    """Обрабатывает команду пользователя на добавление товара
                /add <name> <amount> <cost>"""
    command = helpers.is_valid(message.text, r"/add\s+.+\s+\d{1,16}\s+\d{1,16}")
    if command:
        status = DATABASE_MANAGER.add_product(command[1], command[2], command[3])
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text=f'Товар с таким именем уже есть в базе.\n'
                     f'ID существующего товара: {status}'
            )
            return
        product_id = DATABASE_MANAGER.get_next_product_id() - 1
        BOT.send_message(
            chat_id=message.chat.id,
            text=f'Товар добавлен в базу данных.\n'
                 f'ID товара:  {product_id}\n'
                 f'Имя товара: {command[1]}\n'
                 f'Количество: {command[2]}\n'
                 f'Стоимость:  {command[3]}\n'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='комманда введена неверно.\n'
             'формат команды: /add <name> <amount> <cost>"'
    )


@BOT.message_handler(
    commands=['setv'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['setv'])
)
def set_value_of_product(message):
    """Обрабатывает команду пользователя на изменение цены товара"""
    if helpers.is_valid(message.text, r"/add\s+.+\s+\d{1,16}\s+\d{1,16}"):
        BOT.send_message(chat_id=message.chat.id, text='access successful')
        return
    BOT.send_message(chat_id=message.chat.id,
                     text='комманда введена неверно.\n'
                          'формат команды: /add <name> <amount> <cost>"')


@BOT.message_handler(
    commands=['seta'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['seta'])
)
def set_amount_of_product(message):
    """Обрабатывает команду пользователя на изменение количества товара"""
    pass


@BOT.message_handler(
    commands=['del'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['del'])
)
def del_product(message):
    """Обрабатывает команду пользователя на удаление товара"""
    pass


@BOT.message_handler(
    commands=['info'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['info'])
)
def info_of_product(message):
    """Обрабатывает команду пользователя на получение информации о товаре"""
    BOT.send_message(chat_id=message.chat.id, text='access successful')
    pass
