import sqlite3
import config
import logging
import math

logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


class DatabaseManager:
    def __init__(self, filename):
        self.connection = sqlite3.connect(database=filename, check_same_thread=False)
        logging.info("database is open")
        self.cursor = self.connection.cursor()
        self.init_database()

    def init_database(self):
        self.cursor.execute("SELECT `name` FROM sqlite_master WHERE type='table'")
        tables_list = list(map(lambda tuple_obj: tuple_obj[0], self.cursor.fetchall()))
        if "goods" not in tables_list:
            self.cursor.execute("CREATE TABLE `goods`"
                                "(`id` INT PRIMARY KEY, `name` TEXT, `amount` INT, `s_price` INT, `p_price` INT)")

        self.cursor.execute("SELECT max(`id`), count(`id`) FROM `goods`")
        found = self.cursor.fetchone()
        self.next_product_id = (1 if found[0] is None else int(found[0]) + 1)
        self.amount_goods = found[1]

        if "codes" not in tables_list:
            self.cursor.execute("CREATE TABLE `codes` (`code` TEXT, `role` BOOLEAN)")
            self.cursor.execute("INSERT INTO `codes` VALUES(?, ?)",
                                (config.admin_code, 2))
            self.cursor.execute("INSERT INTO `codes` VALUES(?, ?)",
                                (config.employer_code, 1))

        if "journal" not in tables_list:
            self.cursor.execute("CREATE TABLE `journal` (`id` INT PRIMARY KEY, `amount_sales` INT, `sold_on` INT, "
                                "`amount_purchases` INT, `purchased_on` INT)")

        self.connection.commit()

    def check_auth(self, code):
        code = code.strip()
        self.cursor.execute("SELECT `code`, `role` FROM `codes` WHERE `code` = ?",
                            (code,))
        res = self.cursor.fetchone()
        if res is None:
            return 0
        return res[1]

    def add_product(self, name, amount, s_price, p_price):
        """Если продукт с таким именем уже есть - добавления не происходит и возвращается id продукта
                   иначе происходит добавление продукта и возвращается False"""
        self.cursor.execute("SELECT `id` FROM `goods` WHERE `name` = ?",
                            (name,))
        found = self.cursor.fetchone()
        if found is not None:
            return found[0]
        self.cursor.execute("INSERT INTO `goods` VALUES(?, ?, ?, ?, ?)",
                            (self.next_product_id, name, amount, s_price, p_price))
        self.connection.commit()
        self.next_product_id += 1
        self.amount_goods += 1
        return False

    def del_product(self, _id):
        """Если продукта с таким id нет - удаление невозможно и возвращается False,
                   иначе происходит удаление и возвращается запись о продукте"""
        # если товара с таким id нет - возвращаем False
        found = self.__get_product(_id)
        if not found:
            return False
        self.cursor.execute("DELETE FROM `goods` WHERE `id` = ?",
                            (_id,))
        self.connection.commit()
        self.amount_goods -= 1
        return found

    # set sell price
    def setsp(self, _id, value):
        """Если продукта с таким id нет - изменить стоимость продажи невозможно и возвращаем False,
                 в противном случае возвращается запись о продукте (обновленную)"""
        found = self.__get_product(_id)
        if not found:
            return False
        self.cursor.execute("UPDATE `goods` SET `s_price` = ? WHERE `id` = ?", (value, _id))
        self.connection.commit()
        return self.__get_product(_id)

    # set purchase price
    def setpp(self, _id, value):
        """Если продукта с таким id нет - изменить стоимость покупки невозможно и возвращаем False,
                   в противном случае возвращается запись о продукте (обновленную)"""
        found = self.__get_product(_id)
        if not found:
            return False
        self.cursor.execute("UPDATE `goods` SET `p_price` = ? WHERE `id` = ?", (value, _id))
        self.connection.commit()
        return self.__get_product(_id)

    # set amount
    def seta(self, _id, amount):
        """Если продукта с таким id нет - изменить количество невозможно и возвращаем False,
                         в противном случае возвращается запись о продукте (обновленную)"""
        found = self.__get_product(_id)
        if not found:
            return False
        self.cursor.execute("UPDATE `goods` SET `amount` = ? WHERE `id` = ?", (amount, _id))
        self.connection.commit()
        return self.__get_product(_id)

    def get_catalog_page(self, page):
        """Возвращает запрашиваемую страницу из каталога (количество страниц в каталоге определяется в config)
                Если страницы в каталоге нет возвращается False"""
        self.cursor.execute("SELECT * FROM `goods` LIMIT ? OFFSET ?",
                            (config.catalog_offset, (page - 1) * config.catalog_offset))
        found = self.cursor.fetchall()
        if len(found) == 0:
            return False
        return found

    def get_journal_page(self, page):
        """None"""
        self.cursor.execute("SELECT * FROM `journal` LIMIT ? OFFSET ?",
                            (config.journal_offset, (page - 1) * config.journal_offset))
        found = self.cursor.fetchall()
        if len(found) == 0:
            return False
        return found

    def get_next_product_id(self):
        return self.next_product_id

    def get_amount_pages(self):
        return math.ceil(self.amount_goods / config.catalog_offset)

    def get_amount_goods(self):
        return self.amount_goods

    def close(self):
        self.connection.close()
        logging.info("database is closed")

    # HELPER FUNCTIONS:
    def __get_product(self, _id) -> bool | list:
        """Возвращает запись о продукте из БД, если продукта с указанным ID нет - вернет False"""
        self.cursor.execute("SELECT * FROM `goods` WHERE `id` = ? ",
                            (_id,))
        found = self.cursor.fetchone()
        if found is not None:
            return found
        return False

    def __get_product_name(self, _id):
        found = self.__get_product(_id)
        if found:
            return found[1]
        return found
