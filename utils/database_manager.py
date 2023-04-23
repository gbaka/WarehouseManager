import sqlite3
import config
import logging

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
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `goods`(`id` INT, `name` TEXT, `amount` INT, `cost` INT)")
        self.cursor.execute("SELECT max(`id`) FROM `goods`")
        found = self.cursor.fetchone()
        self.next_product_id = (1 if found[0] is None else int(found[0]) + 1)
        if "codes" not in tables_list:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `codes` (`code` TEXT, `role` BOOLEAN)")
            self.cursor.execute("INSERT INTO `codes` VALUES(?, ?)",
                                (config.admin_code, 2))
            self.cursor.execute("INSERT INTO `codes` VALUES(?, ?)",
                                (config.employer_code, 1))
        self.connection.commit()

    def check_auth(self, code):
        code = code.strip()
        self.cursor.execute("SELECT `code`, `role` FROM `codes` WHERE `code` = ?",
                            (code,))
        res = self.cursor.fetchone()
        if res is None:
            return 0
        return res[1]

    def add_product(self, name, amount, cost):
        """Если продукт с таким именем уже есть - добавления не происходит и возвращается id продукта
                   иначе происходит добавление продукта и возвращается False"""
        self.cursor.execute("SELECT `id` FROM `goods` WHERE `name` = ?",
                            (name,))
        found = self.cursor.fetchone()
        if found is not None:
            return found[0]
        self.cursor.execute("INSERT INTO `goods` VALUES(?, ?, ?, ?)",
                            (self.next_product_id, name, amount, cost))
        self.connection.commit()
        self.next_product_id += 1
        return False

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


    def get_next_product_id(self):
        return self.next_product_id

    def close(self):
        self.connection.close()
        logging.info("database is closed")
