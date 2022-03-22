import sqlite3


class CoreDB:
    def __init__(self, database_name):
        self.is_user_registered = None
        self.connection = sqlite3.connect(database_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def insert_pydantic_scheme(self, scheme, table_name):
        columns = ", ".join(scheme.dict().keys())  # As str "column1, column2, ... , columnN"
        values = list(scheme.dict().values())  # As list [value1, value2, ... , value]
        sql = f"INSERT INTO {table_name} " \
              f"({columns}) " \
              f"VALUES ({(len(values) * '?, ')[:-2]})"  # Forming a list of values (?, ?, ... ?) for secured SQL request
        self.cursor.execute(sql, values)
        self.connection.commit()

    def __del__(self):
        self.connection.close()
