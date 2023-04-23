import sqlite3
import config
import logging


logging.basicConfig(level=logging.INFO, filename="logs.txt", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s")
CONNECTION = sqlite3.connect(config.db_name, check_same_thread=False)


class DatabaseManager:
    def __init__(self, filename):
        self.connection = sqlite3.connect(filename)
        self.cursor = self.connection.cursor()

    def init_database(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables_list = list(map(lambda tuple_obj: tuple_obj[0], self.cursor.fetchall()))
        if "goods" not in tables_list:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS ?(? INT, ? TEXT, ? INT, ? INT)",
                                ("goods", "id", "name", "amount", "cost"))
        if "codes" not in tables_list:
            self.cursor.execute("CREATE TABLE IF NOT EXISTS ?(? TEXT, ? BOOLEAN)",
                                ("codes", "code", "role"))
            self.cursor.execute(f"INSERT INTO ? VALUES(?, ?)",
                                ("codes", config.admin_code, 1))
            self.cursor.execute(f"INSERT INTO ? VALUES(?, ?)",
                                ("codes", config.employer_code, 0))
        self.connection.commit()

    def check_auth(self, code):
        code = code.strip()
        self.cursor.execute(f"SELECT ?, ? FROM ? WHERE ? = ?",
                            ("code", "role", "codes", "code", code))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return -1
        return res[0][1]

    def close(self):
        self.connection.close()

        self.cursor.et

def init_database():
    cursor = CONNECTION.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables_list = list(map(lambda tuple_obj: tuple_obj[0], cursor.fetchall()))
    if "goods" not in tables_list:
        cursor.execute("CREATE TABLE IF NOT EXISTS goods(id INT, name TEXT, amount INT, cost INT)")
    if "codes" not in tables_list:
        cursor.execute("CREATE TABLE IF NOT EXISTS codes(code TEXT, role BOOLEAN)")
        cursor.execute(f"INSERT INTO codes VALUES(\"{config.admin_code}\", 1)")
        cursor.execute(f"INSERT INTO codes VALUES(\"{config.employer_code}\", 0)")
    CONNECTION.commit()
    cursor.close()


def check_auth(code):
    code = code.strip()
    cursor = CONNECTION.cursor()
    cursor.execute(f"SELECT code, role FROM codes WHERE code=\"{code}\"")
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        return -1
    return result[0][1]








