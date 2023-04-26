from telebot import types
import re
import config


def is_valid(command_string, template, parse_markdown=True):
    """Проверяет, соответствует ли данная строка regex шаблону.
       Если да - возвращает разбиение строки, иначе False"""
    command_string = command_string.strip()
    check = re.search(template, command_string)
    if check is None:
        return False
    command = check[0]
    if parse_markdown:
        command = to_markdown_correct(command)
    return command.split()


def create_catalog_page(catalog_page: list, page: int, goods_amount: int, for_admin: bool = False) -> str:
    title = f'📁 *{page}-ая страница каталога:*\n'
    info = f'_*всего товаров в каталоге: {goods_amount}_\n\n'
    text = ''
    for record in catalog_page:
        text += f'_ID товара:_  {record[0]}\n'
        text += f'_Имя товара:_  "{to_markdown_correct(record[1])}"\n'
        text += f'_Количество:_ {record[2]}\n'
        text += f'_\0:_ {record[3]}\n'
        text += f'_Стоимость покупки:_ {record[4]}\n'
        text += '\n'
    if for_admin:
        text = text.replace('\0', 'Стоимость продажи')
        return title + info + text
    text = text.replace('\0', 'Стоимость')
    split_text = text.split('\n')
    del split_text[4::6]
    return title + info + '\n'.join(split_text)


def create_journal_page(journal_page: list, page: int, records_amount: int) -> str:
    title = f'📔 *{page}\-ая страница журнала учета:*\n'
    info = f'_\*всего записей в журнале: {records_amount}_\n\n'
    text = ''
    for record in journal_page:
        text += f'_ID товара:_  {record[0]}\n'
        text += f'_Имя товара:_  "{to_markdown_correct(record[1], 2)}"\n'
        text += f'_Количество продаж:_  {record[2]}\n'
        text += f'_Количество закупок:_  {record[4]}\n'
        text += f'_Доход от продаж:_  {record[3]}\n'
        text += f'_Расход на закупки:_  {record[5]}\n'
        profit = int(record[3])-int(record[5])
        profit = '\-' + str(-profit) if profit < 0 else profit
        text += f'_*Прибыль:*_  *{profit}*\n'
        text += '\n'
    return title + info + text



def create_flip_keyboard(page: int, max_page: int, callback_label: str):
    if page > max_page or page < 1:
        return False
    markup = types.InlineKeyboardMarkup()
    left = types.InlineKeyboardButton('ᐊ', callback_data=f'{callback_label} {page - 1}')
    current = types.InlineKeyboardButton(f"{page}/{max_page}", callback_data='None')
    right = types.InlineKeyboardButton('ᐅ', callback_data=f'{callback_label} {page + 1}')
    markup.add(left, current, right)
    return markup


def create_start_keyboard():
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton("Каталог")
    item2 = types.KeyboardButton("Справка")
    markup.add(item1, item2)
    return markup

def create_action_keyboar(callback_data):
    print(f"cb is {callback_data}")
    markup = types.InlineKeyboardMarkup()
    sell = types.InlineKeyboardButton('Продать', callback_data=f'sell {callback_data}')
    buy = types.InlineKeyboardButton('Купить', callback_data=f'buy {callback_data}')
    markup.add(sell, buy)
    return markup


def to_markdown_correct(string, markdown_v = 1):
    string = string.replace('_', '\_')
    string = string.replace('*', '\*')
    string = string.replace('~', '\~')
    string = string.replace('`', '\`')
    if markdown_v == 2:
        string = string.replace('.', '\.')
        string = string.replace('-', '\-')
    return string


def get_info(user_id, access_level):
    '''Возвращает текст умной справки
    (в зависимости от уровня доступа юзера)'''
    info = config.info['title']
    for i in range(access_level + 1):
        info += config.info[i]
    return info
