import sqlite3
import config
import logging

logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


class DatabaseManager:
    next_product_id = 0

    def __init__(self, filename):
        self.connection = sqlite3.connect(database=filename, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.init_database()

    def init_database(self):
        self.cursor.execute("SELECT `name` FROM sqlite_master WHERE type='table'")
        tables_list = list(map(lambda tuple_obj: tuple_obj[0], self.cursor.fetchall()))
        if "goods" not in tables_list:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `goods`(`id` INT, `name` TEXT, `amount` INT, `cost` INT)")
        self.cursor.execute("SELECT max(`id`) FROM `goods`")
        found = self.cursor.fetchone()
        self.next_product_id = (0 if len(found) == 0 else found[0]) + 1
        if "codes" not in tables_list:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `codes` (`code` TEXT, `role` BOOLEAN)")
            self.cursor.execute("INSERT INTO `codes` VALUES(?, ?)",
                                (config.admin_code, 1))
            self.cursor.execute("INSERT INTO `codes` VALUES(?, ?)",
                                (config.employer_code, 0))
        self.connection.commit()

    def check_auth(self, code):
        code = code.strip()
        self.cursor.execute("SELECT `code`, `role` FROM `codes` WHERE `code` = ?",
                            (code,))
        res = self.cursor.fetchone()
        if res is None:
            return -1
        return res[1]

    def add_product(self, name, amount, cost):
        """Если продукт с таким именем уже есть - добавления не происходит и возвращается id продукта
                   иначе происходит добавление продукта и возвращается True"""
        self.cursor.execute("SELECT `id` FROM `goods` WHERE `name` = ",
                            (name,))
        found = self.cursor.fetchone()
        if len(found) != 0:
            return found[0]
        self.cursor.execute("INSERT INTO `goods` VALUES(?, ?, ?, ?)",
                            (name, amount, cost, self.next_product_id))
        self.connection.commit()
        self.next_product_id += 1
        return True

    def del_product(self, _id):
        """Если продукта с таким id нет - удаление невозможно и возвращается False,
                   иначе происходит удаление и возвращается True"""
        # если товара с таким id нет - возвращаем False
        if not self.__is_exist(_id):
            return False
        self.cursor.execute("DELETE FROM `goods` WHERE `id` = ?",
                            (_id,))
        self.connection.commit()
        return True

    def setv(self, _id, value):
        """Если продукта с таким id нет - изменить стоимость невозможно и возвращаем False,
                        в противном случае возвращаем True"""
        if not self.__is_exist(_id):
            return False
        self.cursor.execute("UPDATE `goods` SET `cost` = ? WHERE `id` = ?", (value, _id))
        return True

    def __is_exist(self, _id):
        """Возвращает True, если в базе есть товар с указанным id"""
        self.cursor.execute("SELECT `id` FROM `goods` WHERE `id` = ",
                            (_id,))
        found = self.cursor.fetchone()
        return len(found) != 0

    def close(self):
        self.connection.close()
