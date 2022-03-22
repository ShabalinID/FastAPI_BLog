from models import User
from database.core import CoreDB


class UserDatabase(CoreDB):
    async def get_user_name_id(self, username):
        sql = "SELECT user_id " \
              "FROM users " \
              "WHERE username=:username"
        self.cursor.execute(sql, {"username": username})
        result = self.cursor.fetchone()[0]
        return result

    async def username_is_taken(self, username):
        sql = "SELECT username " \
              "FROM users " \
              "WHERE username=:username"
        self.cursor.execute(sql, {"username": username})
        result = self.cursor.fetchone()
        return result

    async def insert_new_user(self, user: User):
        table_name = "users"
        self.insert_pydantic_scheme(table_name=table_name,
                                    scheme=user)

    async def get_user_password(self, username):
        sql = "SELECT hashed_password " \
              "FROM users " \
              "WHERE username=:username"
        self.cursor.execute(sql, {"username": username})
        result = self.cursor.fetchone()[0]
        return result
