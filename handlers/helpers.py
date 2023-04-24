from telebot import types
from utils.account_manager import AccountManager
import re

ACCOUNT_MANAGER = AccountManager()


def check_access(user_id, required_access):
    print(user_id)
    return ACCOUNT_MANAGER.get_access_level(user_id) >= required_access


def is_valid(command_string, template):
    """Проверяет, соответствует ли данная строка regex шаблону.
       Если да - возвращает разбиение строки, иначе False"""
    command_string = command_string.strip()
    print(command_string)
    check = re.search(template, command_string)
    print(check)

    if check is None:
        return False
    return check[0].split()


def create_catalog_page(catalog_page: str, page: int) -> str:
    text = f'{page}-ая страница каталога:\n'
    for record in catalog_page:
        text += f'ID товара:  {record[0]}\n'
        text += f'Имя товара: {record[1]}\n'
        text += f'Количество: {record[2]}\n'
        text += f'Стоимость:  {record[3]}\n'
        text += '\n'
    return text

def create_page_keyboard(page: int, max_page: int):
    if page > max_page or page < 1:
        return False
    markup = types.InlineKeyboardMarkup()
    left = types.InlineKeyboardButton('<-',callback_data=f'to page {page-1}')
    current = types.InlineKeyboardButton(f"{page}/{max_page}", callback_data='None')
    right = types.InlineKeyboardButton('->', callback_data=f'to page {page+1}')
    markup.add(left, current, right)
    return markup

