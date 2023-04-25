import telebot
import config
import handlers.helpers as helpers
from utils.database_manager import DatabaseManager
from utils.account_manager import AccountManager

BOT = telebot.TeleBot(token=config.TOKEN,parse_mode='Markdown')
DATABASE_MANAGER = DatabaseManager(config.db_name)
ACCOUNT_MANAGER = AccountManager()


@BOT.message_handler(
    commands=['start'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['start'])
)
def start(message):
    """Начало работы с ботом"""
    BOT.send_message(
        chat_id=message.chat.id,
        text="*🛠 Слава труду!*\nВыбирай кнопку, которая тебя интересует.",
        reply_markup=helpers.create_start_keyboard(),
        parse_mode='Markdown'
    )


@BOT.message_handler(
    commands=['auth', 'register', 'reg'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['auth'])
)
def auth(message):
    """Авторизует пользователя по ключу
             /auth <key>"""
    command = helpers.is_valid(message.text, r"/(auth|register|reg)\s+.+(\s+|$)")
    if command:
        current_access_level = ACCOUNT_MANAGER.get_access_level(message.from_user.id)
        if current_access_level:
            BOT.send_message(
                chat_id=message.chat.id,
                text=f"⚙️ *Вы уже авторизованы как {'работник' if current_access_level == 1 else 'администратор'}*\n"
                     f"Воспользуйтесь командой /unauth чтобы выйти из системы."
            )
            return
        new_access_level = DATABASE_MANAGER.check_auth(command[1])
        if new_access_level == 0:
            BOT.send_message(
                chat_id=message.chat.id,
                text="❌ *Введен неверный ключ.*\nПожалуйста, повторите команду."

            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text=f"🔑 *Вы вошли в систему как {'работник' if new_access_level == 1 else 'администратор'}*"
        )
        ACCOUNT_MANAGER.auth(message.from_user.id, new_access_level)
        ACCOUNT_MANAGER.show()
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             'Формат команды:\n'
             '`/auth <key>`'
    )


@BOT.message_handler(
    commands=['unauth', 'unregister', 'unreg'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['unauth'])
)
def unauth(message):
    """Исключает пользователя из списка авторизованных
             /unauth <key>"""
    current_access_level = ACCOUNT_MANAGER.get_access_level(message.from_user.id)
    if not current_access_level:
        BOT.send_message(
            chat_id=message.chat.id,
            text=f'⚙️ *Вы и так неавторизованный пользователь*'
        )
        return
    ACCOUNT_MANAGER.unauth(message.from_user.id)
    BOT.send_message(
        chat_id=message.chat.id,
        text=f'🚪 *Вы успешно вышли из аккаунта*'
    )

@BOT.message_handler(
    commands=['add'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['add'])
)
def add_product(message):
    """Обрабатывает команду пользователя на добавление товара
                /add <name> <amount> <sell_price> <purchase_price>"""
    command = helpers.is_valid(message.text, r"/add\s+.+\s+\d{1,16}\s+\d{1,16}\s+\d{1,16}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.add_product(command[1], command[2], command[3], command[4])
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text=f'⚙️ *Товар с таким именем уже есть в базе.*\n'
                     f'ID существующего товара: {status}'
            )
            return
        product_id = DATABASE_MANAGER.get_next_product_id() - 1
        BOT.send_message(
            chat_id=message.chat.id,
            text='✅ *Товар добавлен в базу.*\n\n'
                 f'_ID товара:_  {product_id}\n'
                 f'_Имя товара:_  "{command[1]}"\n'
                 f'_Количество:_  {command[2]}\n'
                 f'_Стоимость продажи:_  {command[3]}\n'
                 f'_Стоимость покупки:_  {command[4]}\n'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             'Формат команды:\n'
             '`/add <name> <amount> <sell> <purchase>`'

    )


@BOT.message_handler(
    commands=['setsp', 'setpp'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['setp'])
)
def set_price_of_product(message):
    """Обрабатывает команду пользователя на изменение цены продажи товара
                  (/setsp|/setpp) <ID> <new_cost> """
    command = helpers.is_valid(message.text, r"/(setsp|setpp)\s+\d{1,8}\s+\d{1,16}(\s+|$)")
    if command:
        if command[0] == '/setsp':
            status = DATABASE_MANAGER.setsp(command[1], command[2])
            price_type = 'продажи'
        else:
            status = DATABASE_MANAGER.setpp(command[1], command[2])
            price_type = 'покупки'
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                text=f'✅ *Цена {price_type} товара успешно изменена*\n\n'
                     f'_ID товара:_  {status[0]}\n'
                     f'_Имя товара:_  "{status[1]}"\n'
                     f'_Количество:_  {status[2]}\n'
                     f'_Стоимость покупки:_  {status[3]}\n'
                     f'_Стоимость продажи:_  {status[4]}\n'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Товара с таким ID нет в базе*'
        )
        return
    command = message.text.split()[0]
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             f'Формат команды:\n'
             f'`{command} <ID> <price>`'
    )


@BOT.message_handler(
    commands=['seta'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['seta'])
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
                text='✅ *Количество товара успешно изменено*\n\n'
                     f'_ID товара:_  {status[0]}\n'
                     f'_Имя товара:_  "{status[1]}"\n'
                     f'_Количество:_  {status[2]}\n'
                     f'_Стоимость:_  {status[3]}\n'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Товара с таким ID нет в базе*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             'Формат команды:'
             '`/seta <ID> <amount>`'
    )


@BOT.message_handler(
    commands=['del'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['del'])
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
                text='🗑️ *Товар был удален.*\n\n'
                     f'_ID товара:_  {status[0]}\n'
                     f'_Имя товара:_  "{status[1]}"\n'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Товара с таким ID нет в базе*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             'Формат команды:'
             '`/del <ID>`'
    )
    pass


# @BOT.message_handler(
#     commands=['info'],
#     func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['info'])
# )
# def info_of_product(message):
#     """Обрабатывает команду пользователя на получение информации о товаре"""
#     BOT.send_message(chat_id=message.chat.id, text='access successful')
#     pass

@BOT.message_handler(
    commands=['info'],
func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['info'])
)
def info(message):
    user_id = message.from_user.id
    BOT.send_message(
        chat_id=message.chat.id,
        text=helpers.get_info(user_id, ACCOUNT_MANAGER.get_access_level(user_id))
    )


@BOT.message_handler(
    commands=['catalog'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['catalog'])
)
def show_catalog(message):
    """Обрабатывает команду пользователя на отображения страницы каталога
               /catalog <page=1>"""
    command = helpers.is_valid(message.text, r"(/catalog|Каталог)((\s+\d+)|\s*)(\s+|$)")
    if command:
        page = 1 if len(command) == 1 else int(command[1])
        page = 1 if page == 0 else page
        status = DATABASE_MANAGER.get_catalog_page(page)
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                reply_markup=helpers.create_page_keyboard(page, DATABASE_MANAGER.get_amount_pages()),
                text=helpers.create_catalog_page(
                    status, page, DATABASE_MANAGER.get_amount_goods(),
                    ACCOUNT_MANAGER.is_admin(message.from_user.id)
                )
            )
            return
        if page == 1:
            BOT.send_message(
                chat_id=message.chat.id,
                text='📂 *Каталог пуст*'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Указанной страницы нет в каталоге*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно*.\n\n'
             'Формат команды:\n'
             '`/catalog <page=0>`'
    )

@BOT.message_handler(
    commands=['myrole'],
    func=lambda call: ACCOUNT_MANAGER.check_access(call.from_user.id, config.commands_access['myrole'])
)
def get_my_role(message):
    access_level = ACCOUNT_MANAGER.get_access_level(message.from_user.id)
    match access_level:
        case 0:
            role = "Пользователь"
        case 1:
            role = "Работник"
        case 2:
            role = "Администратор"
        case _:
            role = "Unknown"
    BOT.send_message(
        chat_id=message.chat.id,
        text=f"⚙️ Ваша роль: *{role}*"
    )


@BOT.message_handler(
    content_types=['text']
)
def keyboard_response(message):
    if message.chat.type == 'private':
        if message.text == 'Каталог':
            show_catalog(message)
        if message.text == 'Справка':
            info(message)


@BOT.callback_query_handler(
    func=lambda call: ACCOUNT_MANAGER.check_access(call.from_user.id, config.commands_access['catalog'])
)
def flip_page(call):
    command = helpers.is_valid(call.data, r'to page \d+')
    if command:
        to_page = int(command[2])
        if 1 <= to_page <= DATABASE_MANAGER.get_amount_pages():
            page_record = DATABASE_MANAGER.get_catalog_page(to_page)
            max_page = DATABASE_MANAGER.get_amount_pages()
            BOT.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=helpers.create_page_keyboard(to_page, max_page),
                text=helpers.create_catalog_page(
                    page_record, to_page, DATABASE_MANAGER.get_amount_goods(),
                    ACCOUNT_MANAGER.is_admin(call.from_user.id)
                )
            )
    BOT.answer_callback_query(callback_query_id=call.id)
