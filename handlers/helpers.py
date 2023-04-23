from utils.account_manager import AccountManager
import re

ACCOUNT_MANAGER = AccountManager()


def check_access(user_id, required_id):
    return ACCOUNT_MANAGER.get_access_level(user_id) >= required_id


def is_valid(command_string, template):
    """Проверяет, соответствует ли данная строка regex шаблону.
       Если да - возвращает разбиение строки, иначе False"""
    command_string = command_string.strip()
    check = re.search(template, command_string)
    if check is None:
        return False
    return check[0].split()

