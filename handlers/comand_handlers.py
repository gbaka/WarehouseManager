import telebot
import config
import handlers.helpers as helpers
from utils.database_manager import DatabaseManager
from utils.account_manager import AccountManager

BOT = telebot.TeleBot(token=config.TOKEN, parse_mode='Markdown')
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
    command = helpers.is_valid(message.text, r"/add\s+\S+\s+\d{1,16}\s+\d{1,16}\s+\d{1,16}(\s+|$)")
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
            text='⚙️ *Товара с таким ID нет в каталоге*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             'Формат команды:'
             '`/del <ID>`'
    )


@BOT.message_handler(
    commands=['product'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['product'])
)
def show_product_info(message):
    """Обрабатывает команду пользователя на получение сводной информации о товаре
                         /product <ID>"""
    command = helpers.is_valid(message.text, r"/product\s+\d{1,8}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.get_all_of_product(command[1])
        if status:
            from_catalog, from_journal = status
            title = "📝 *Полные данные по товару:*\n\n"
            part_1 = ['*Данные из каталога:*', 'Данных нет\n']
            part_2 = ['*Данные из журнала учета:*', 'Данных нет\n']
            if from_catalog:
                _id = from_catalog[0]
                name = from_catalog[1]
                part_1[1] = f"_Число товара на складе:_ {from_catalog[2]}\n" \
                            f"_Цена продажи товара:_ {from_catalog[3]}\n" \
                            f"_Цена закупки товара:_ {from_catalog[4]}\n\n"
            if from_journal:
                _id = from_journal[0]
                name = from_journal[1]
                income = int(from_journal[3])
                expense = int(from_journal[5])
                part_2[1] = f"_Число продаж товара:_  {from_journal[2]}\n" \
                            f"_Число закупок товара:_  {from_journal[4]}\n" \
                            f"_Доход от продаж:_  {income}\n" \
                            f"_Расход на закупки:_  {expense}\n" \
                            f"_Прибыль:_  {income - expense}\n"
            name = helpers.to_markdown_correct(name)
            sub_title = f'_ID товара:_  {_id}\n' \
                        f'_Имя товара:_  {name}\n\n'
            text = title + sub_title + '\n'.join(part_1) + '\n'.join(part_2)
            print(_id)
            BOT.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=helpers.create_action_keyboar(_id)
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *По товару с данным ID нет информации*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             'Формат команды:'
             '`/product <ID>`'
    )


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
                reply_markup=helpers.create_flip_keyboard(page, DATABASE_MANAGER.get_amount_catalog_pages(), 'catalog'),
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
    commands=['journal'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['journal'])
)
def show_journal(message):
    """Обрабатывает команду пользователя на отображения страницы журнала продаж и закупок
               /journal <page=1>"""
    command = helpers.is_valid(message.text, r"/journal((\s+\d+)|\s*)(\s+|$)")
    if command:
        page = 1 if len(command) == 1 else int(command[1])
        page = 1 if page == 0 else page
        ###
        status = DATABASE_MANAGER.get_journal_page(page)
        if status:
            BOT.send_message(
                chat_id=message.chat.id,
                reply_markup=helpers.create_flip_keyboard(page, DATABASE_MANAGER.get_amount_journal_pages(), 'journal'),
                text=helpers.create_journal_page(status, page, DATABASE_MANAGER.get_amount_journal_records()),
                parse_mode='MarkdownV2'
            )
            return
        if page == 1:
            BOT.send_message(
                chat_id=message.chat.id,
                text='📂 *Журнал учета пуст*'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Указанной страницы нет в журнале учета*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно*.\n\n'
             'Формат команды:\n'
             '`/journal <page=1>`'
    )


@BOT.message_handler(
    commands=['buy'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['buy'])
)
def buy_product(message):
    """/buy <id> <amount>"""
    command = helpers.is_valid(message.text, r"/buy\s+\d{1,8}\s+[1-9]\d{0,15}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.buy_product(command[1], command[2])
        if status:
            purchase_price = status[4]
            BOT.send_message(
                chat_id=message.chat.id,
                text=f'✅ *Вы успешно закупили {command[2]} единиц товара "{status[1]}":*\n\n'
                     f'_ID товара:_  {status[0]}\n'
                     f'_Имя товара:_  "{status[1]}"\n'
                     f'_Стоимость закупки товара:_  {status[4]}\n'
                     f'_Закуплено штук:_  {command[2]}\n'
                     f'_*Расход на закупку:*_  *{purchase_price * int(command[2])}*\n',
                parse_mode='MarkdownV2'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Товара с таким ID нет в каталоге*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно*.\n\n'
             'Формат команды:\n'
             '`/buy <id> <amount>`'
    )


@BOT.message_handler(
    commands=['sell'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['sell'])
)
def sell_product(message):
    """/sell <id> <amount>"""
    command = helpers.is_valid(message.text, r"/sell\s+\d{1,8}\s+[1-9]\d{0,15}(\s+|$)")
    if command:
        status = DATABASE_MANAGER.sell_product(command[1], command[2])
        match status:
            case 1:
                BOT.send_message(
                    chat_id=message.chat.id,
                    text='⚙️ *Товара с таким ID нет в каталоге*'
                )
                return
            case 2:
                BOT.send_message(
                    chat_id=message.chat.id,
                    text='⚙️ *Нельзя продать товара больше, чем имеется на складе*'
                )
                return
            case _:
                sell_price = status[3]
                BOT.send_message(
                    chat_id=message.chat.id,
                    text=f'✅ *Вы успешно продали {command[2]} единиц\(ы\) товара "{status[1]}":*\n\n'
                         f'_ID товара:_  {status[0]}\n'
                         f'_Имя товара:_  "{status[1]}"\n'
                         f'_Стоимость продажи товара:_  {status[3]}\n'
                         f'_Продано штук:_  {command[2]}\n'
                         f'_*Доход от продажи:*_  *{sell_price * int(command[2])}*\n',
                    parse_mode='MarkdownV2'
                )
                return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно*.\n\n'
             'Формат команды:\n'
             '`/sell <id> <amount>`'
    )


@BOT.message_handler(
    commands=['setas', 'setso', 'setap', 'setpo'],
    func=lambda mes: ACCOUNT_MANAGER.check_access(mes.from_user.id, config.commands_access['setj'])
)
def set_journal(message):
    command = helpers.is_valid(message.text, r"/(setas|setso|setap|setpo)\s+\d{1,8}\s+\d{1,16}(\s+|$)")
    if command:
        match command[0]:
            case '/setas':
                status = DATABASE_MANAGER.journal_set(command[1], command[2], "`amount_sales`")
                mes = "✅ *Количество продаж товара успешно изменено:*"
            case '/setso':
                status = DATABASE_MANAGER.journal_set(command[1], command[2], "`sold_on`")
                mes = "✅ *Доход от продаж товара успешно изменён:*"
            case '/setap':
                status = DATABASE_MANAGER.journal_set(command[1], command[2], "`amount_purchases`")
                mes = "✅ *Количество покупок товара успешно изменено:*"
            case '/setpo':
                status = DATABASE_MANAGER.journal_set(command[1], command[2], "`purchased_on`")
                mes = "✅ *Расход на закупки товара успешно изменён:*"
            case _:
                status = False
                mes = None
        if status:
            _profit = int(status[3]) - int(status[5])
            _profit = '\-' + str(-_profit) if _profit < 0 else _profit
            BOT.send_message(
                chat_id=message.chat.id,
                text=f'{mes}\n\n'
                     f'_ID товара:_  {status[0]}\n'
                     f'_Имя товара:_  "{status[1]}"\n'
                     f'_Количество продаж:_  {status[2]}\n'
                     f'_Количество закупок:_  {status[4]}\n'
                     f'_Доход от продаж:_  {status[3]}\n'
                     f'_Расход на закупки:_  {status[5]}\n'
                     f'_*Прибыль:*_  *{_profit}*\n',
                parse_mode='MarkdownV2'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Товара с таким ID нет в журнале учета*'
        )
        return
    command = message.text.split()[0]
    val = "value" if command in ['/setso', '/setpo'] else "amount"
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Команда введена неверно.*\n\n'
             f'Формат команды:\n'
             f'`{command} <id> <{val}>`'
    )


@BOT.message_handler(
    commands=['profit'],
    func=lambda call: ACCOUNT_MANAGER.check_access(call.from_user.id, config.commands_access['profit'])
)
def profit(message):
    income, expense, profit = DATABASE_MANAGER.calculate_profit()
    BOT.send_message(
        chat_id=message.chat.id,
        text="📈 *Данные по выручке:*\n\n"
             f"_Cуммарный доход:_  {income}\n"
             f"_Cуммарный расход:_  {expense}\n"
             f"_Суммарная прибыль:_  {profit}\n\n"
             f"_*Для более детальной информации используйте команду_ /journal"
    )


@BOT.message_handler(
    commands=['clearj'],
    func=lambda call: ACCOUNT_MANAGER.check_access(call.from_user.id, config.commands_access['clearj'])
)
def clear_journal(message):
    DATABASE_MANAGER.clear_journal()
    BOT.send_message(
        chat_id=message.chat.id,
        text="🗑️ *Журнал учета был успешно очищен*"
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
    func=lambda call: True
)
def flip_page(call):
    command = helpers.is_valid(call.data, r'[A-Za-z]+((\s+\d+)|s*)')
    command = call.data.split()
    print(command)
    user_id = call.from_user.id
    if command[0] == 'catalog' and ACCOUNT_MANAGER.check_access(user_id, config.commands_access['catalog']):
        to_page = int(command[1])
        max_page = DATABASE_MANAGER.get_amount_catalog_pages()
        if 1 <= to_page <= max_page:
            page_record = DATABASE_MANAGER.get_catalog_page(to_page)
            BOT.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=helpers.create_flip_keyboard(to_page, max_page, 'catalog'),
                text=helpers.create_catalog_page(
                    page_record, to_page, DATABASE_MANAGER.get_amount_goods(),
                    ACCOUNT_MANAGER.is_admin(call.from_user.id)
                )
            )
    elif command[0] == 'journal' and ACCOUNT_MANAGER.check_access(user_id, config.commands_access['journal']):
        to_page = int(command[1])
        max_page = DATABASE_MANAGER.get_amount_journal_pages()
        if 1 <= to_page <= max_page:
            page_record = DATABASE_MANAGER.get_journal_page(to_page)
            BOT.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=helpers.create_flip_keyboard(to_page, max_page, 'journal'),
                parse_mode="MarkdownV2",
                text=helpers.create_journal_page(
                    page_record, to_page,
                    DATABASE_MANAGER.get_amount_journal_records()
                )
            )
    elif command[0] == 'sell':
        product = DATABASE_MANAGER.get_product_name(command[1])
        mes = BOT.send_message(
            chat_id=call.message.chat.id,
            text=f'Сколько единиц товара "{product}" вы хотите продать?'
        )
        BOT.register_next_step_handler(mes, handle_button_sell, int(command[1]))
    elif command[0] == 'buy':
        product = DATABASE_MANAGER.get_product_name(command[1])
        mes = BOT.send_message(
            chat_id=call.message.chat.id,
            text=f'Сколько единиц товара "{product}" вы хотите купить?'
        )
        BOT.register_next_step_handler(mes, handle_button_buy, int(command[1]))
    BOT.answer_callback_query(callback_query_id=call.id)


def handle_button_sell(message, _id):
    amount = helpers.is_valid(message.text, r"^\s*\d+(\s+|$)")
    amount = int(amount[0]) if amount else 0
    if amount:
        status = DATABASE_MANAGER.sell_product(_id, amount)
        match status:
            case 1:
                BOT.send_message(
                    chat_id=message.chat.id,
                    text='⚙️ *Товара с таким ID нет в каталоге*'
                )
                return
            case 2:
                BOT.send_message(
                    chat_id=message.chat.id,
                    text='⚙️ *Нельзя продать товара больше, чем имеется на складе*'
                )
                return
            case _:
                sell_price = status[3]
                BOT.send_message(
                    chat_id=message.chat.id,
                    text=f'✅ *Вы успешно продали {amount} единиц\(ы\) товара "{status[1]}":*\n\n'
                         f'_ID товара:_  {status[0]}\n'
                         f'_Имя товара:_  "{status[1]}"\n'
                         f'_Стоимость продажи товара:_  {status[3]}\n'
                         f'_Продано штук:_  {amount}\n'
                         f'_*Доход от продажи:*_  *{sell_price * amount}*\n',
                    parse_mode='MarkdownV2'
                )
                return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Количество должно быть положительным числом*.'
    )


def handle_button_buy(message, _id):
    amount = helpers.is_valid(message.text, r"^\s*\d+(\s+|$)")
    amount = int(amount[0]) if amount else 0
    if amount:
        status = DATABASE_MANAGER.buy_product(_id, amount)
        if status:
            purchase_price = status[4]
            BOT.send_message(
                chat_id=message.chat.id,
                text=f'✅ *Вы успешно закупили {amount} единиц товара "{status[1]}":*\n\n'
                     f'_ID товара:_  {status[0]}\n'
                     f'_Имя товара:_  "{status[1]}"\n'
                     f'_Стоимость закупки товара:_  {status[4]}\n'
                     f'_Закуплено штук:_  {amount}\n'
                     f'_*Расход на закупку:*_  *{purchase_price * amount}*\n',
                parse_mode='MarkdownV2'
            )
            return
        BOT.send_message(
            chat_id=message.chat.id,
            text='⚙️ *Товара с таким ID нет в каталоге*'
        )
        return
    BOT.send_message(
        chat_id=message.chat.id,
        text='❌ *Количество должно быть положительным числом*.'
    )
