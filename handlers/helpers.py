from telebot import types
import re
import config



def is_valid(command_string, template):
    """Проверяет, соответствует ли данная строка regex шаблону.
       Если да - возвращает разбиение строки, иначе False"""
    command_string = command_string.strip()
    check = re.search(template, command_string)
    if check is None:
        return False
    return check[0].split()


def create_catalog_page(catalog_page: str, page: int, goods_amount: int, for_admin: bool = False) -> str:
    title = f'📁 *{page}-ая страница каталога:*\n'
    info = f'_*всего товаров в каталоге: {goods_amount}_\n\n'
    text = ''
    for record in catalog_page:
        text += f'_ID товара:_  {record[0]}\n'
        text += f'_Имя товара:_  "{record[1]}"\n'
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




def create_page_keyboard(page: int, max_page: int):
    if page > max_page or page < 1:
        return False
    markup = types.InlineKeyboardMarkup()
    left = types.InlineKeyboardButton('<-',callback_data=f'to page {page-1}')
    current = types.InlineKeyboardButton(f"{page}/{max_page}", callback_data='None')
    right = types.InlineKeyboardButton('->', callback_data=f'to page {page+1}')
    markup.add(left, current, right)
    return markup

def create_start_keyboard():
    markup = types.ReplyKeyboardMarkup()
    item1 = types.KeyboardButton("Каталог")
    item2 = types.KeyboardButton("Справка")
    markup.add(item1, item2)
    return markup


def get_info(user_id, access_level):
    '''Возвращает текст умной справки
    (в зависимости от уровня доступа юзера)'''
    info = config.info['title']
    for i in range(access_level+1):
        info += config.info[i]
    return info