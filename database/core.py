import sqlite3
from database.messages import MessagesDatabase
from database.auth import AuthDatabase


class SqliteDatabase(MessagesDatabase, AuthDatabase):
    def __init__(self, database_name='sqlite.db'):
        self.is_user_registered = None
        self.connection = sqlite3.connect(database_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()
