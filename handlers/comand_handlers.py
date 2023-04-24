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
    BOT.send_message(chat_id=message.chat.id, text="Здравствуйте. авторизация /auth <key>")


@BOT.message_handler(
    commands=['auth', 'register', 'reg'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['auth'])
)
def auth(message):
    """Авторизует пользователя по ключу
             /auth <key>"""
    command = helpers.is_valid(message.text, r"/(auth|register|reg)\s+.+(\s+|$)")
    if command:
        current_access_level = helpers.ACCOUNT_MANAGER.get_access_level(message.from_user.id)
        if current_access_level:
            BOT.send_message(
                chat_id=message.chat.id,
                text=f"Вы уже авторизованы как {'работник' if current_access_level == 1 else 'администратор'}\n"
                     f"Воспользуйтесь командой /unauth чтобы выйти из системы"
            )
            return
        new_access_level = DATABASE_MANAGER.check_auth(command[1])
        if new_access_level == 0:
            mes = BOT.send_message(
                chat_id=message.chat.id,
                text="Введен неверный ключ. Пожалуйста, повторите команду:"
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text=f"Вы вошли в систему как {'работник' if new_access_level == 1 else 'администратор'}"
        )
        helpers.ACCOUNT_MANAGER.auth(message.from_user.id, new_access_level)
        helpers.ACCOUNT_MANAGER.show()
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='Команда введена неверно.\n'
             'формат команды: /auth <key>'
    )


@BOT.message_handler(
    commands=['unauth', 'unregister', 'unreg'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['unauth'])
)
def unauth(message):
    """Исключает пользователя из списка авторизованных
             /unauth <key>"""
    command = helpers.is_valid(message.text, r"/(unauth|unregister|unreg)\s*")
    current_access_level = helpers.ACCOUNT_MANAGER.get_access_level(message.from_user.id)
    if not current_access_level:
        BOT.send_message(
            chat_id=message.chat.id,
            text=f'Вы и так неавторизованный пользователь'
        )
        return
    helpers.ACCOUNT_MANAGER.unauth(message.from_user.id)
    BOT.send_message(
        chat_id=message.chat.id,
        text=f'Вы успешно вышли из аккаунта'
    )


def add_product(message):
    """Обрабатывает команду пользователя на добавление товара
                /add <name> <amount> <cost>"""
    command = helpers.is_valid(message.text, r"/add\s+.+\s+\d{1,16}\s+\d{1,16}(\s+|$)")
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
            text='Товар добавлен в базу данных.\n'
                 f'ID товара:  {product_id}\n'
                 f'Имя товара: {command[1]}\n'
                 f'Количество: {command[2]}\n'
                 f'Стоимость:  {command[3]}\n'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='Комманда введена неверно.\n'
             'формат команды: /add <name> <amount> <cost>'
    )


@BOT.message_handler(
    commands=['setv'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['setv'])
)
def set_value_of_product(message):
    """Обрабатывает команду пользователя на изменение цены товара
                  /setv <ID> <new_cost>"""
    command = helpers.is_valid(message.text, r"/setv\s+\d{1,8}\s+\d{1,16}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.setv(command[1], command[2])
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text='Цена товара успешно изменена\n'
                     f'ID товара:  {status[0]}\n'
                     f'Имя товара: {status[1]}\n'
                     f'Количество: {status[2]}\n'
                     f'Стоимость:  {status[3]}\n'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='Товара с таким ID нет в базе'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='Команда введена неверно.\n'
             'формат команды: /setv <ID> <new_cost>'
    )


@BOT.message_handler(
    commands=['seta'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['seta'])
)
def set_amount_of_product(message):
    """Обрабатывает команду пользователя на изменение количества товара
                      /seta <ID> <new_amount>"""
    command = helpers.is_valid(message.text, r"/seta\s+\d{1,8}\s+\d{1,16}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.seta(command[1], command[2])
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text='Количество товара успешно изменено\n'
                     f'ID товара:  {status[0]}\n'
                     f'Имя товара: {status[1]}\n'
                     f'Количество: {status[2]}\n'
                     f'Стоимость:  {status[3]}\n'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='Товара с таким ID нет в базе'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='Команда введена неверно.\n'
             'формат команды: /seta <ID> <new_amount>'
    )


@BOT.message_handler(
    commands=['del'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['del'])
)
def del_product(message):
    """Обрабатывает команду пользователя на удаление товара
                     /del <ID>"""
    command = helpers.is_valid(message.text, r"/del\s+\d{1,8}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.del_product(command[1])
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text='Товар был удален.\n'
                     f'ID товара:  {status[0]}\n'
                     f'Имя товара: {status[1]}\n'
                     f'Количество: {status[2]}\n'
                     f'Стоимость:  {status[3]}\n'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='В базе нет товара с указанным ID'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='Команда введена неверно.\n'
             'формат команды: /del <ID>'
    )
    pass


@BOT.message_handler(
    commands=['info'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['info'])
)
def info_of_product(message):
    """Обрабатывает команду пользователя на получение информации о товаре"""
    BOT.send_message(chat_id=message.chat.id, text='access successful')
    pass


@BOT.message_handler(
    commands=['catalog'],
    func=lambda mes: helpers.check_access(mes.from_user.id, config.commands_access['catalog'])
)
def show_catalog(message):
    """Обрабатывает команду пользователя на отображения страницы каталога
               /catalog <page=1>"""
    command = helpers.is_valid(message.text, r"/catalog((\s+\d+)|\s*)(\s+|$)")
    if command:
        page = 1 if len(command) == 1 else int(command[1])
        page = 1 if page == 0 else page
        status = DATABASE_MANAGER.get_catalog_page(page)
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text=helpers.create_catalog_page(status,page),
                reply_markup=helpers.create_page_keyboard(page, DATABASE_MANAGER.get_amount_pages())
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='Указанной страницы нет в каталоге'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='Команда введена неверно.\n'
             'формат команды: /catalog <page=0>'
    )

# func=lambda call: print('acces is ',)

@BOT.callback_query_handler(
    func=lambda call: helpers.check_access(call.from_user.id, config.commands_access['catalog'])
)
def flip_page(call):
    command = helpers.is_valid(call.data, r'to page \d+')
    if command:
        to_page = int(command[2])
        if 1 <= to_page <= DATABASE_MANAGER.get_amount_pages():
            page_record = DATABASE_MANAGER.get_catalog_page(to_page)
            max_page = DATABASE_MANAGER.get_amount_pages()
            BOT.edit_message_text(
                text=helpers.create_catalog_page(page_record, to_page),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=helpers.create_page_keyboard(to_page, max_page)
            )
