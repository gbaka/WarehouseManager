TOKEN = "6039881807:AAEeNEQWIGQp8sh6K0kYBZvvc66KSX-Pkn8"
db_name = "warehouse.db"
admin_code = "admin"
employer_code = "employer"
delay = 0.75
catalog_offset = 5
commands_access = {
    "start":   0,
    "add":     1,
    "setp":    2,
    "seta":    2,
    "del":     2,
    "info":    0,
    "catalog": 0,
    "auth":    0,
    "unauth":  0,
    "myrole":  0
}


info = {
       'title': '_Список команд бота\n\n'
                '*на количество доступных вам команд влияет ваш уровень доступа_\n\n',

       0: '*Общедоступные команды*:\n\n'
          '`/start`\n'
          '- начать работу бота\n\n'
          '`/info`\n'
          '- список команд бота\n\n'
          '`/catalog <page=1>`\n'
          '- вывод каталога товаров (по умолчанию выводится первая страница каталога)\n\n'
          '`/auth <key>`\n'
          '- аутентификация по ключу, позволяет перейти в режим '
          'работника или администратора\n\n'
          '`/unauth`\n'
          '- выход из режима работника/администратора\n\n'
          '`/myrole`\n'
          '- ваш текущий уровень доступа\n\n\n',

       1: '*Команды работников:*\n\n'
          '`/sell <id> <amount>`\n'
          '- продажа товара с идентификатором id в размере amount штук '
          '(продажа по цене продажи)\n\n'
          '`/buy <id> <amount>`'
          '- покупка товара с идентификатором id в размере amount штук '
          '(покупка по цене покупки)\n\n\n',

       2: '*Команды Администраторов:*\n\n'
          '`/add <name> <amount> <sell> <purchase>`\n'
          '- добавляет в базу товар с именем name в количестве amount, '
          'sell - цена продажи, purchase - цена покупки\n\n'
          '`/setsp <id> <price>`\n'
          '- изменяет цену продажи товара с идентификатором id на price\n\n'
          '`/setpp <id> <price>`\n'
          '- изменяет цену покупки товара с идентификатором id на price\n\n'
          '`/seta <id> <amount>`\n'
          '- изменяет количество товара с идентификатором id на amount\n\n'
          '`/del <id>`\n'
          '- удаляет товар с идентификатором id из базы\n\n\n'
}
